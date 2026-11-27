# 8. New Data Structures That Fusion Could Introduce

(ChatGPT, 2026-11-27 - section 8 of [DataStructures_Guide.md](DataStructures_Guide.md), which stops at 8.1; a review with a limited view - CLAUDE.md Rule 3c)

This is where Fusion can become interesting.

I would not introduce dozens of new structures just to make Fusion look
different. Instead, Fusion should introduce structures that solve
problems existing languages often leave to application developers.

The following are 12 proposals, expanding on the Fusion Structured
Memory Architecture.

## 8.1 Data Stack `<Single>`

**Status: Existing Fusion concept**

A Data Stack dedicated to storing one specific object type.

```fusion
DataStack<Single<Customer>>
```

Example storage:

```text
DataStack<Customer>
├── Customer A
├── Customer B
├── Customer C
├── Customer D
├── Customer E
└── FREE
```

Characteristics:

-   Stores one defined object type.
-   Individual objects can be allocated and released.
-   Can use optimised memory layouts.
-   Can reuse released memory slots.
-   Can provide type-specific indexing.

Example:

```fusion
customers = DataStack<Single<Customer>>

customerA = customers.allocate()
customerB = customers.allocate()

customers.release(customerA)
```

Potential uses:

-   Customers.
-   Products.
-   Orders.
-   Employees.
-   Sensor readings.

**Recommendation:** This should be one of Fusion's primary storage
types. Internally, it could use indexed slots or slab allocation,
depending on object size and lifetime requirements.

## 8.2 Data Stack `<Mixed>`

**Status: Existing Fusion concept**

A general-purpose storage area that supports multiple known object
types.

```fusion
DataStack<Mixed>
```

Example contents:

```text
DataStack<Mixed>
├── Customer
├── Order
├── String
├── Integer
├── Product
├── DateTime
└── Invoice
```

Characteristics:

-   Different types can coexist.
-   Every object retains its type information.
-   Supports individual allocation and release.
-   Can support different object sizes.
-   Can use handles to identify objects.

Potential uses:

-   Application runtime.
-   Dynamic business objects.
-   Temporary processing.
-   Collections containing different object types.

**Important:** Mixed must not mean untyped. Fusion should still know
exactly what every object contains, including the information needed to
destroy it safely.

## 8.3 Data Stack `<General>`

**Status: Existing Fusion concept**

A more flexible storage area for dynamically generated or unpredictable
objects.

```fusion
DataStack<General>
```

Potential uses:

-   Runtime-generated objects.
-   Reflection.
-   Plugin data.
-   Dynamically loaded modules.
-   Unknown object layouts.

Possible distinction from Mixed:

  Mixed                                      General
  ------------------------------------------ -----------------------------------
  Known types                                Runtime-determined types
  Type metadata available                    Dynamic type resolution
  More predictable layouts                   Potentially unpredictable layouts
  More compiler optimisation opportunities   More runtime management

This distinction needs to be validated during implementation. Otherwise,
Mixed and General risk becoming redundant concepts.

## 8.4 Data Stack `<Grid>`

**Status: Existing concept -- expanded**

A storage structure divided into independently allocated slots, rather
than one continuous sequence.

Example: a three-column, four-row grid.

```text
          Column 1   Column 2   Column 3

Row 1       [ A ]      [ B ]      [ C ]
Row 2       [ D ]      [FREE]     [ E ]
Row 3       [ F ]      [FREE]     [ G ]
Row 4       [ H ]      [ I ]      [FREE]
```

Characteristics:

-   Each slot can be individually allocated.
-   Each slot can be individually released.
-   Released slots can be reused.
-   Objects do not need to be stored sequentially.
-   Slots can hold objects of a defined size or references to external
    allocations.

Potential uses:

-   Game entities.
-   Customer records.
-   Dynamic application objects.
-   Simulation objects.
-   Robotics data.

**Technical consideration:** A grid is a logical organisation, not
necessarily a physical two-dimensional memory layout. Internally, Fusion
could implement it using pages containing arrays of slots. This allows
the grid to grow while keeping allocation and reclamation predictable.

## 8.5 Data Stack `<Temporal>`

**Status: New Fusion proposal**

A storage structure organised around time and object lifetime.

```fusion
DataStack<Temporal>
```

Objects could be grouped according to:

-   Creation time.
-   Expiry time.
-   Last-access time.
-   Retention policy.

Example:

```text
Temporal Storage
├── 0–1 minute       Short-lived objects
├── 1–10 minutes     Temporary objects
├── 10–60 minutes    Session objects
└── Permanent        Long-lived objects
```

Potential uses:

-   API responses.
-   Session data.
-   Temporary calculations.
-   Cache entries.
-   Log processing.

An interesting feature would be automatic expiry:

```fusion
DataStack<Temporal> {
    defaultLifetime: 10.minutes
}
```

Fusion could maintain expiry buckets or a priority queue rather than
scanning every object continuously.

## 8.6 Data Stack `<Versioned>`

**Status: New Fusion proposal**

A structure that keeps multiple versions of an object.

Example:

```text
Customer 1001

Version 1
    Name = ABC Trading

Version 2
    Name = ABC Distribution

Version 3
    Name = ABC Holdings
```

Rather than immediately overwriting previous data, Fusion could preserve
previous versions.

Characteristics:

-   Version history.
-   Snapshot support.
-   Historical reads.
-   Optional rollback.
-   Shared unchanged object data.

Potential uses:

-   Undo/redo.
-   Audit history.
-   Configuration management.
-   Transactions.
-   Concurrent readers.

Example:

```fusion
customer = customers.get(id)

customer.update {
    name = "ABC Distribution"
}

customer.history()
customer.restore(version: 1)
```

Persistent data structures and copy-on-write techniques are worth
investigating for implementation.

## 8.7 Data Stack `<Shared>`

**Status: New Fusion proposal**

Storage specifically designed for objects accessed by multiple Services.

```fusion
DataStack<Shared<Customer>>
```

Characteristics:

-   Multiple services can access the same data.
-   Explicit read/write permissions.
-   Defined lifetime and ownership.
-   Controlled synchronisation.
-   Optional immutable snapshots.

Potential uses:

-   Shared application configuration.
-   Common lookup tables.
-   Shared customer information.
-   Server session information.

Example:

```fusion
Service CustomerReader {
    access customers.read
}

Service CustomerUpdater {
    access customers.write
}
```

Avoid making Shared an unrestricted way around Fusion's ownership model.
The objective should be controlled sharing, not unrestricted shared
memory.

## 8.8 Data Stack `<Stream>`

**Status: New Fusion proposal**

A storage structure designed for continuously arriving data.

```fusion
DataStack<Stream<SensorReading>>
```

Characteristics:

-   Continuous data ingestion.
-   Configurable capacity.
-   Multiple independent consumers.
-   Consumer read positions.
-   Backpressure.
-   Optional overwrite of old records.

Example:

```text
Stream
├── Reading 001
├── Reading 002
├── Reading 003
├── Reading 004
├── Reading 005
└── Reading 006
```

Potential uses:

-   Sensor data.
-   Network packets.
-   Logging.
-   Event processing.
-   Financial market data.

An important difference from a Queue is that a Stream can allow multiple
consumers to independently read the same sequence. For example, one
service processes readings while another service records them.

## 8.9 Data Stack `<Indexed>`

**Status: New Fusion proposal**

A structure where objects are automatically indexed according to
selected properties.

```fusion
DataStack<Indexed<Customer>>
```

Example:

```fusion
DataStack<Indexed<Customer>> {
    index CustomerID using Hash
    index CustomerName using BTree
    index Province using Hash
}
```

Potential characteristics:

-   Multiple indexes.
-   Fast lookup.
-   Range searching.
-   Automatic index maintenance.
-   Type-aware indexing.

Potential uses:

-   In-memory databases.
-   Business applications.
-   Large object collections.
-   Reporting.

**Important consideration:** Indexes consume additional memory and must
be updated when indexed fields change. Fusion should define whether
indexed fields are immutable, automatically maintained, or updated
through controlled mutation.

## 8.10 Data Stack `<Transactional>`

**Status: New Fusion proposal**

A storage domain supporting atomic changes across multiple objects.

Example:

```fusion
transaction.run {
    accountA.balance = accountA.balance - 500
    accountB.balance = accountB.balance + 500
}
```

Either both changes succeed or neither does.

Characteristics:

-   Atomic updates.
-   Rollback.
-   Consistent snapshots.
-   Isolation policies.
-   Conflict detection.

Potential uses:

-   Financial applications.
-   Inventory management.
-   Order processing.
-   Database operations.

Transactions should remain distinct from Service ownership. A Service
controls execution and access; a transaction controls the consistency of
a group of changes.

## 8.11 Data Stack `<Spatial>`

**Status: New Fusion proposal**

A storage structure designed around spatial relationships.

Possible internal structures:

-   KD-Tree.
-   Quadtree.
-   Octree.
-   R-Tree.

Example:

```fusion
DataStack<Spatial<GameObject>> {
    dimensions: 3
    index: Octree
}
```

Potential uses:

-   Games.
-   Robotics.
-   Simulations.
-   Geographic applications.
-   Collision detection.
-   3D environments.

This would be useful for applications that continuously search for
nearby objects.

## 8.12 Data Stack `<Compressed>`

**Status: New Fusion proposal**

A storage structure optimised for reducing memory consumption.

Possible techniques:

-   Dictionary encoding.
-   Run-length encoding.
-   Delta encoding.
-   Bit packing.
-   Column-oriented storage.

Example:

```fusion
DataStack<Compressed<SensorReading>> {
    encoding: Delta
}
```

Potential uses:

-   Large datasets.
-   Analytics.
-   Historical measurements.
-   Scientific applications.
-   Data archiving.

The trade-off is that accessing or modifying individual values may
require decompression or reconstruction.

------------------------------------------------------------------------

## Summary of Section 8

  Data Stack        Status               Main purpose
  ----------------- -------------------- ----------------------------------------
  `Single<T>`       Existing             One known object type
  `Mixed`           Existing             Multiple known object types
  `General`         Existing             Dynamic or unpredictable objects
  `Grid`            Existing, expanded   Independently allocated slots
  `Temporal`        Proposed             Time-based lifetime and expiry
  `Versioned`       Proposed             Historical object versions
  `Shared`          Proposed             Controlled multi-service access
  `Stream`          Proposed             Continuous data and multiple consumers
  `Indexed`         Proposed             Automatic object indexing
  `Transactional`   Proposed             Atomic multi-object changes
  `Spatial`         Proposed             Spatial and geometric searching
  `Compressed`      Proposed             Memory-efficient data storage

**Architectural recommendation:** Treat these as storage capabilities or
specialised storage abstractions, not necessarily twelve unrelated
physical memory implementations. Several can be implemented by combining
existing allocators, indexes, metadata and access policies.
