# Fusion Threading and Concurrency Specification

Description: Comprehensive guide to multithreading, concurrency, and parallel programming in Fusion. This document covers thread management, synchronization, channels, and compiler optimizations for concurrent code.

---

## Overview

Description: Fusion's approach to concurrent programming.

* **Philosophy**: Hybrid model supporting both message passing and shared memory
* **Default Strategy**: Message passing via channels (Go-style)
* **Alternative Strategy**: Traditional shared memory with locks (when needed)
* **Compiler Role**: Automatic thread analysis, lock insertion, and optimization
* **IDE Integration**: Visual representation of threading structure

---

## Threading Hierarchy

Description: Layers of concurrent execution from system to channels.

---

### Complete Hierarchy

System → Process → Thread Pool → Thread → Task/Goroutine → Channel/Queue

* **System**: Operating system managing all processes
     * Schedules processes
     * Manages system resources
     * Handles process creation/destruction

* **Process**: Isolated execution unit
     * Own memory space
     * Contains one or more threads
     * Heavyweight (expensive to create)
     * Inter-process communication required

* **Thread Pool**: Collection of reusable threads
     * Managed by runtime
     * Reduces thread creation overhead
     * Automatically sized based on CPU cores
     * Handles task distribution

* **Thread**: OS-level execution unit
     * Shares memory with other threads in process
     * Own call stack and registers
     * Scheduled by OS
     * Can access shared data (needs synchronization)

* **Task/Goroutine**: User-space lightweight thread
     * Managed by language runtime
     * Multiplexed onto OS threads
     * Very cheap to create (thousands possible)
     * Cooperative scheduling

* **Channel**: Communication queue
     * Thread-safe message passing
     * Can be buffered or unbuffered
     * Enables ownership transfer
     * No locks needed for communication

---

## Thread Creation and Management

Description: How to create and control threads in Fusion.

---

### Creating Threads

```
// Basic thread creation
Thread function workerThread()
    print("Thread started")
    // Do work
    return

// Start thread
Thread t = Thread.create(workerThread)
t.start()
t.join()  // Wait for completion

// Thread with parameters
Thread function processData(int start, int end)
    for i in range(start, end)
        process(i)
    end loop
    return

Thread t = Thread.create(lambda: processData(0, 100))
t.start()
```

---

### Goroutines (Lightweight Threads)

```
// Creating goroutine - very lightweight
go workerFunction()

// Goroutine with parameters
go processData(0, 100)

// Anonymous goroutine
go lambda:
    print("Processing in background")
    doWork()

// Multiple goroutines
for i in range(10)
    go lambda:
        processItem(i)
end loop
```

---

### Thread Pools

```
// Create thread pool (automatic sizing)
ThreadPool pool = ThreadPool.create()

// Submit tasks to pool
for i in range(100)
    pool.submit(lambda: processItem(i))
end loop

// Wait for all tasks to complete
pool.waitAll()

// Shutdown pool
pool.shutdown()

// Custom thread pool size
ThreadPool pool = ThreadPool.create(threads = 8)
```

---

## Message Passing with Channels

Description: Safe communication between threads without shared memory.

---

### Channel Basics

```
// Create unbuffered channel
Channel<int> ch = Channel.create<int>()

// Create buffered channel (capacity 10)
Channel<int> buffered = Channel.create<int>(capacity = 10)

// Send to channel (blocks if full)
ch.send(42)

// Receive from channel (blocks if empty)
int value = ch.receive()

// Non-blocking send (returns false if full)
bool sent = ch.trySend(42)

// Non-blocking receive (returns option type)
Option<int> value = ch.tryReceive()
```

---

### Producer-Consumer Pattern

```
// Producer thread
void function producer(Channel<Task> taskQueue)
    for i in range(100)
        Task task = createTask(i)
        taskQueue.send(task)
    end loop
    taskQueue.close()  // Signal no more data

// Consumer thread
void function consumer(Channel<Task> taskQueue)
    while not taskQueue.isClosed()
        Task task = taskQueue.receive()
        if task is null
            break  // Channel closed and empty
        processTask(task)
    end loop

// Setup
Channel<Task> queue = Channel.create<Task>(capacity = 10)
go producer(queue)
go consumer(queue)
```

---

### Select Statement

Description: Wait on multiple channels simultaneously.

```
Channel<int> ch1 = Channel.create<int>()
Channel<int> ch2 = Channel.create<int>()

select
    case value = ch1.receive():
        print("Received from ch1: {value}")
    
    case value = ch2.receive():
        print("Received from ch2: {value}")
    
    case timeout(1000):  // 1 second timeout
        print("Timeout!")
    
    default:
        print("No data available")
```

---

## Shared Memory Synchronization

Description: Traditional approach when message passing doesn't fit.

---

### Mutex Locks

```
// Create mutex
Mutex lock = Mutex()

// Manual locking
lock.acquire()
sharedVariable += 1
lock.release()

// Better: using statement (automatic unlock)
using lock
    sharedVariable += 1
    doWork()
// Automatically unlocked
```

---

### Read-Write Locks

```
// Create read-write lock
RWLock rwlock = RWLock()

// Multiple readers allowed simultaneously
using rwlock.read()
    int value = sharedData
// Read lock released

// Single writer (exclusive)
using rwlock.write()
    sharedData = newValue
// Write lock released
```

---

### Atomic Operations

```
// Atomic operations (lock-free)
Atomic<int> counter = Atomic<int>(0)

// Atomic increment
counter.incrementAndGet()  // Returns new value
counter.getAndIncrement()  // Returns old value

// Atomic compare-and-swap
bool success = counter.compareAndSwap(expected = 5, newValue = 10)

// Other atomic operations
counter.add(10)
counter.subtract(5)
int value = counter.get()
counter.set(100)
```

---

## Try-With-Resources (Automatic Locking)

Description: Compiler-managed resource locking for safety.

---

### Automatic Resource Locking

```
// File locking - automatic
using file = openFile("data.txt")
    file.write("Data")
    file.flush()
// File closed and unlocked automatically

// Object locking - automatic
class BankAccount
    private float balance
    
    void function deposit(float amount)
        using this  // Lock entire object
            balance += amount
        // Unlocked automatically
    
    void function withdraw(float amount)
        using this
            if balance >= amount
                balance -= amount
        // Unlocked

// Multiple threads can safely call deposit/withdraw
```

---

### Custom Resource Management

```
// Custom resource with automatic cleanup
class Database
    void function connect()
        // Connection logic
    
    void function disconnect()
        // Cleanup logic
    
    void function query(string sql)
        // Query logic

// Using with automatic cleanup
using db = Database()
    db.connect()
    db.query("SELECT * FROM users")
// db.disconnect() called automatically
```

---

## Compiler Analysis and Optimization

Description: How the compiler analyzes and optimizes concurrent code.

---

### Thread Section Analysis

Description: Compiler breaks code into sections for threading analysis.

**What the Compiler Does**

* Identifies shared resources (variables, objects, files)
* Determines which functions can run in parallel
* Detects potential race conditions
* Inserts necessary locks automatically
* Optimizes lock granularity
* Prevents deadlocks through lock ordering

**Code Sectioning Example**

```
void function processData(List<int> data)
    // Section 1: Read-only (can parallelize)
    int sum = 0
    for value in data
        sum += value
    end loop
    
    // Section 2: Write to shared resource (needs lock)
    globalCounter += sum
    
    // Section 3: Independent work (can parallelize)
    saveToFile(sum)

// Compiler analysis:
// - Section 1: Can run in parallel (multiple threads)
// - Section 2: Requires lock on globalCounter
// - Section 3: Can run in parallel (different files)
```

---

### Visual Threading in IDE

Description: IDE shows threading structure visually.

**IDE Features**

* Color-coded thread sections
* Lock visualization
* Shared resource highlighting
* Potential race condition warnings
* Thread flow diagrams
* Performance hotspots

**Example IDE View**

```
[Thread-Safe Section - Green]
void function calculateStatistics(Data data)
    // Independent calculations
    float mean = data.mean()
    float stddev = data.stddev()

[Requires Lock - Yellow]
    // Writing to shared resource
    globalStats.update(mean, stddev)

[Parallel-Safe - Green]
    // Independent I/O
    saveResults(mean, stddev)
```

---

### Compiler-Generated Thread File

Description: Compiled output includes threading metadata.

**Threading Metadata File (.fthread)**

```
// game.fusion.fthread
{
    "functions": [
        {
            "name": "processData",
            "threadSafe": false,
            "sharedResources": ["globalCounter"],
            "locks": ["globalCounter.lock"],
            "parallelizable": ["section1", "section3"],
            "sequential": ["section2"]
        }
    ],
    "sharedResources": {
        "globalCounter": {
            "type": "int",
            "accessPattern": "read-write",
            "lockStrategy": "mutex"
        }
    }
}
```

---

## Advanced Threading Patterns

Description: Common concurrent programming patterns.

---

### Worker Pool Pattern

```
Channel<Task> taskQueue = Channel.create<Task>(capacity = 100)
int numWorkers = 8

// Start workers
for i in range(numWorkers)
    go lambda:
        while true
            Task task = taskQueue.receive()
            if task is null
                break
            task.execute()
        end loop
end loop

// Submit tasks
for i in range(1000)
    taskQueue.send(createTask(i))
end loop

// Signal completion
taskQueue.close()
```

---

### Pipeline Pattern

```
// Stage 1: Read data
Channel<string> rawData = Channel.create<string>(capacity = 10)
go lambda:
    for line in readFile("data.txt")
        rawData.send(line)
    end loop
    rawData.close()

// Stage 2: Process data
Channel<int> processed = Channel.create<int>(capacity = 10)
go lambda:
    while true
        string line = rawData.receive()
        if line is null
            break
        int value = parse(line)
        processed.send(value)
    end loop
    processed.close()

// Stage 3: Save results
go lambda:
    while true
        int value = processed.receive()
        if value is null
            break
        saveToDatabase(value)
    end loop
```

---

### Fan-Out/Fan-In Pattern

```
// Fan-out: Distribute work to multiple workers
Channel<Task> tasks = Channel.create<Task>(capacity = 100)
List<Channel<Result>> results = []

// Create workers
for i in range(8)
    Channel<Result> resultCh = Channel.create<Result>(capacity = 10)
    results.append(resultCh)
    
    go lambda:
        while true
            Task task = tasks.receive()
            if task is null
                break
            Result result = task.execute()
            resultCh.send(result)
        end loop
        resultCh.close()
end loop

// Fan-in: Collect results from all workers
go lambda:
    for resultCh in results
        while true
            Result result = resultCh.receive()
            if result is null
                break
            processResult(result)
        end loop
    end loop
```

---

## Async/Await Pattern

Description: High-level asynchronous programming for I/O operations.

---

### Async Functions

```
// Async function declaration
async Spaceship, Error function downloadShip(string url)
    // Async HTTP request
    Response response = await http.get(url)
    
    if response.statusCode != 200
        return null, Error("HTTP error: {response.statusCode}")
    
    // Async body reading
    string data = await response.readBody()
    
    // Parse and return
    Spaceship ship = parseShipData(data)
    return ship, null

// Calling async function
async void function loadShips()
    Spaceship ship1, Error err1 = await downloadShip("https://api.ships/1")
    Spaceship ship2, Error err2 = await downloadShip("https://api.ships/2")
    
    if err1 or err2
        print("Error loading ships")
        return
    
    print("Ships loaded: {ship1.Name}, {ship2.Name}")
```

---

### Parallel Async

```
// Run multiple async operations in parallel
async void function loadManyShips()
    // Start all downloads in parallel
    List<Task<Spaceship>> tasks = []
    for i in range(10)
        Task<Spaceship> task = async: await downloadShip("https://api.ships/{i}")
        tasks.append(task)
    end loop
    
    // Wait for all to complete
    List<Spaceship> ships = await Task.waitAll(tasks)
    
    print("Loaded {ships.length} ships")
```

---

## Thread Safety Guidelines

Description: Best practices for writing concurrent code.

---

### DO's

* Use channels for communication (message passing)
* Use `using` statement for automatic locking
* Keep critical sections small
* Prefer immutable data
* Use atomic operations when possible
* Design for concurrency from the start
* Test with race detection tools

---

### DON'Ts

* Don't share mutable state without synchronization
* Don't hold locks longer than necessary
* Don't nest locks (can cause deadlocks)
* Don't use global variables without protection
* Don't ignore compiler warnings about races
* Don't use Weak pointers in threaded code (discouraged)

---

## Race Detection and Debugging

Description: Tools for finding and fixing concurrent bugs.

---

### Compile-Time Detection

```
// Compiler flags
fusion build --race-detection game.fusion

// Compiler warns about potential races
class Counter
    private int count
    
    void function increment()
        count += 1  // WARNING: Unsynchronized access to shared field
```

---

### Runtime Detection

```
// Run with race detector
fusion run --race game.fusion

// Reports race conditions
// RACE: Write at 0x12345678 in goroutine 2
// Previous write at 0x12345678 in goroutine 1
```

---

## Performance Optimization

Description: Making concurrent code fast.

---

### Lock-Free Data Structures

```
// Built-in concurrent collections (lock-free)
ConcurrentQueue<Task> queue = ConcurrentQueue<Task>()
ConcurrentMap<string, int> map = ConcurrentMap<string, int>()
ConcurrentSet<int> set = ConcurrentSet<int>()

// Thread-safe operations
queue.enqueue(task)
Task t = queue.dequeue()

map.put("key", 42)
int value = map.get("key")
```

---

### Compiler Optimizations

* **Lock Elision**: Removes unnecessary locks
* **Lock Coarsening**: Combines adjacent locks
* **Escape Analysis**: Determines if data escapes thread
* **Vectorization**: Uses SIMD for parallel operations

---

## Summary

**Key Concepts**

* Threading Hierarchy: System → Process → Thread → Goroutine → Channel
* Message Passing: Prefer channels over shared memory
* Automatic Locking: `using` statement for safety
* Compiler Analysis: Automatic race detection and optimization
* IDE Integration: Visual threading structure
* Async/Await: High-level asynchronous programming

**Default Strategy**: Message passing via channels (safe, clear, performant)

**Alternative Strategy**: Shared memory with locks (when needed for specific patterns)

**Compiler Role**: Analyzes code, inserts locks, prevents races, optimizes performance
