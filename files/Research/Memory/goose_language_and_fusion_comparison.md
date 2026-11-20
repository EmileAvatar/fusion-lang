# Goose Programming Language and Comparison with Other Languages

> **Purpose:** Research notes for the Fusion programming language project.
>
> **Note:** Goose is not Google's Go language. They are separate programming languages.

# Section 1 – Understanding Goose

## 1.1 What is Goose?

[Goose official website](https://aardappel.github.io/goose/)  
[Goose GitHub repository](https://github.com/aardappel/goose)

Goose is a compiled systems programming language developed by Wouter van Oortmerssen.

Its goals include:

- High performance, comparable to or better than C++ and Rust in its published benchmarks.
- Memory safety without a garbage collector.
- No traditional heap allocation.
- No manually written lifetime annotations.
- Predictable memory management.
- Efficient data structures and memory layouts.

Its syntax will look familiar to developers who know C, C++ or Rust.

Its central design decision is that dynamic data lives on compiler-managed data stacks rather than the traditional heap.

## 1.2 Its most interesting feature: No traditional heap

Most programming languages use some form of heap memory for dynamically allocated objects.

**C++ example:**

```cpp
auto* numbers = new int[1000];

// Use numbers

delete[] numbers;
```

**Rust example:**

```rust
let mut numbers = Vec::new();

numbers.push(10);
numbers.push(20);

// Automatically freed when it goes out of scope
```

**Goose example:**

```goose
var numbers: i32[>..] = [];

numbers.push(10);
numbers.push(20);

// Automatically freed when its scope ends
```

Goose uses what it calls *data stacks*. These are not simply the normal function call stack.

- The compiler determines which data stacks are required.
- Each stack has a pointer that advances as data is allocated.
- Dynamic data is stored inline.
- When the scope ends, the stack pointer moves back.
- This releases the allocated memory without individually freeing every object.

Think of this as an arena allocator, but with the compiler controlling allocation and lifetime rules.

## 1.3 Memory safety without lifetime annotations

Rust is famous for its borrow checker and lifetime annotations.

For example, Rust sometimes requires developers to explicitly describe relationships between references.

Goose attempts to infer these relationships automatically.

Its compiler tracks where references originate (their *roots*) and prevents references from surviving longer than the data they refer to.

Conceptually:

```text
Function A
    └── Creates data
          └── Function B references data
```

Function B cannot retain a reference after the owning data has been destroyed.

The compiler checks these relationships rather than relying on the developer to annotate lifetimes.

This is one of Goose's main design advantages.

## 1.4 Data never moves when growing

In many languages, a dynamic array can move when it runs out of capacity.

For example:

1. Allocate an array with capacity 100.
2. Fill the array.
3. Need another element.
4. Allocate a larger array.
5. Copy the old elements.
6. Release the old allocation.

This can invalidate references pointing to the old array.

Goose uses reserved address space and inline data stacks to allow growable arrays to expand without relocating their existing contents.

Consequently, references into those arrays can remain valid while the array grows.

## 1.5 Different array types

Goose has several array forms with different memory behaviours.

| Type | Purpose |
|---|---|
| `T[k]` | Fixed-size array |
| `T[]` | Sized at construction, then fixed |
| `T[..k]` | Inline capacity with a maximum |
| `T[..]` | Variable-sized inline capacity |
| `T[>..]` | Grow-only array |
| `T[>..<]` | Array that can grow and shrink |

The distinction is important because the compiler knows how each array behaves and can enforce the associated memory rules.

For example, a grow-only array is useful when references into the array must remain valid.

Goose also supports variable-sized records and enums, allowing data to be packed efficiently instead of reserving the maximum possible space for every element.

## 1.6 Compilation and execution

Goose supports two main ways of running code:

- **Direct execution:** Goose can run source code in-process using its integrated TinyCC-based backend.
- **Executable compilation:** Goose generates C code, which is compiled and linked using a native C compiler.

It also supports:

- Type checking without building an executable.
- Debug checks for overflow, array bounds and enum tags.
- A language server for IDE integration.
- Packages sourced from directories or Git repositories.
- Native C interoperability.

Example commands:

```bash
goose check program.goose
goose program.goose
goose build program.goose
```

The compiler is implemented in C++ and the generated native programs use a C compilation toolchain.

## 1.7 Concurrency and libraries

Goose supports multithreaded programs, although its direct in-process TinyCC execution mode cannot handle programs using threads; those need to be built as native executables.

Its standard library includes:

- Graphics through SDL3.
- Audio.
- UI and widgets.
- Physics through Box3D.
- Data structures and other utilities.

It is still a young language, with a much smaller ecosystem than Rust, C++ or Java.

## 1.8 Performance claims

The Goose project publishes benchmarks comparing it against C++ and Rust.

Its benchmark summary claims that across 16 benchmarks, Goose achieved:

| Comparison | Reported Goose performance |
|---|---:|
| Versus idiomatic C++ | 3.3× faster |
| Versus hand-optimised C++ | 1.16× faster |
| Versus safe Rust | 1.12× faster |

It also reports lower memory consumption in those comparisons.

These are the project's own benchmark results, not proof that Goose is generally faster than C++ or Rust. Performance depends heavily on the workload, compiler settings and implementation.

## 1.9 Goose's trade-offs

The design is clever, but it comes with restrictions.

- Data lifetimes are constrained by the data-stack model.
- Recursive functions have restrictions around retaining growable data across recursive calls.
- Some variable-sized arrays cannot be indexed directly.
- Certain escaping closures and function-pointer patterns are unsupported.
- The ecosystem and standard library are relatively small.
- It is less suitable for applications that depend on unrestricted, long-lived dynamic object graphs.

These are not necessarily bugs. They are deliberate consequences of the memory model.

# Section 2 – Comparing Goose with Other Major Programming Languages

## 2.1 General comparison

| Feature | C | C++ | Rust | Go | Java | Python | Fusion (planned) | Goose |
|---|---|---|---|---|---|---|---|---|
| Native compilation | Yes | Yes | Yes | Yes | Via JVM/JIT | No (typically) | To be decided | Yes |
| Virtual machine | No | No | No | No | JVM | Runtime/VM | To be decided | No |
| Garbage collection | No | No | No | Yes | Yes | Yes | Planned/design-dependent | No |
| Heap allocation | Manual | Yes | Yes | Yes | Yes | Yes | Planned/design-dependent | No traditional heap |
| Memory safety | Limited | Limited | Strong | Strong runtime safety | Strong managed memory | Managed memory | Compiler-enforced goals | Compiler-enforced |
| Lifetime annotations | No | No | Sometimes | No | No | No | Compiler inference goal | No |
| JIT compilation | No | No | No | No | Yes | Implementation-dependent | Possible | No |
| Interfaces / traits | No | Yes (abstract classes) | Traits | Interfaces | Interfaces | Protocol-like patterns | Traits/interfaces | Variant and case-based dispatch |
| Concurrency | Threads | Threads | Threads | Goroutines | Threads | Threads/async | Services | Threads |
| Automatic memory cleanup | No | RAII | Ownership | GC | GC | GC | Planned resource management | Scope-based |

**Important:** Fusion's entries represent design goals and ideas discussed for the language, not features that are already implemented. Its final memory model and compilation strategy are still decisions to make.

## 2.2 Memory management comparison

This is where Goose is most relevant to Fusion.

| Language | Memory management approach |
|---|---|
| C | Manual allocation and deallocation |
| C++ | Manual allocation, RAII, smart pointers |
| Rust | Ownership and borrowing |
| Go | Garbage collection |
| Java | Garbage collection |
| Python | Reference counting and garbage collection (CPython) |
| Goose | Compiler-managed data stacks, released at scope exit |
| Fusion | Compiler-managed resources and services are being designed |

Consider allocating a collection of 10,000 records:

- **C:** You allocate and free memory yourself.
- **C++:** You use containers and RAII.
- **Rust:** You use ownership and borrowing.
- **Go:** The garbage collector manages object lifetimes.
- **Java:** The garbage collector manages object lifetimes.
- **Python:** Reference counting and garbage collection manage objects.
- **Goose:** The compiler assigns the collection to a data stack and releases its storage at scope exit.
- **Fusion:** We could potentially use compiler-managed resource ownership and services, but we have not committed to a single allocation strategy.

## 2.3 Goose versus Rust

These two languages have similar ambitions:

- Memory safety.
- High performance.
- No garbage collector.
- Native compilation.

The difference is how they achieve memory safety.

**Rust:**

- Ownership and borrowing.
- Lifetime annotations when necessary.
- Heap allocation is supported.
- Flexible data structures.
- Strong ecosystem.

**Goose:**

- Compiler-inferred reference roots.
- No traditional heap.
- Data-stack allocation.
- Scope-based memory release.
- More restrictions on data structures and lifetimes.

Assessment: Rust is more general-purpose. Goose is exploring a more restrictive memory model in exchange for simpler memory management and predictable data layouts.

## 2.4 Goose versus C++

C++ gives developers considerable control over memory.

You can use:

- Stack allocation.
- Heap allocation.
- Custom allocators.
- Memory pools.
- Smart pointers.
- RAII.
- Placement construction.

Goose takes a different approach: rather than giving developers many memory-management options, it restricts the model so the compiler can enforce more guarantees.

C++ is considerably more mature and flexible, but that flexibility can make memory safety harder to guarantee.

## 2.5 Goose versus Go

These names can be confusing. They are unrelated languages with very different designs.

| Feature | Go | Goose |
|---|---|---|
| Main objective | Simplicity and scalable software | Memory-safe systems programming |
| Memory | Garbage collected | Compiler-managed data stacks |
| Heap | Yes | No traditional heap |
| Concurrency | Goroutines and channels | Multithreading |
| Compilation | Native executable | Native executable |
| Ecosystem | Large | Young |
| Typical use | Servers, APIs, infrastructure | Systems and performance-sensitive applications |

Go focuses on making concurrent software relatively simple to develop.

Goose focuses on controlling memory and data layout.

## 2.6 Goose versus Fusion – The interesting comparison

Goose and Fusion are approaching some similar problems, but from different directions.

| Area | Goose | Fusion direction |
|---|---|---|
| Memory ownership | Compiler-managed | Compiler-managed resources |
| Resource lifetime | Scope-based | Resource and service ownership |
| Memory allocation | Data stacks | Still to be designed |
| Garbage collection | None | Still to be decided |
| Concurrency | Threads | Service-based concurrency |
| Shared data | Restricted references | Service can own multiple variables |
| Interfaces | Type and variant-based mechanisms | Traits, objects and interfaces |
| Default implementations | Not its primary design | Planned interface default implementations |
| Resource cleanup | Scope exit | Resource lifetime and expiry/reset |
| Dynamic execution | Direct execution and native compilation | Still to be designed |
| Business rules | Not a primary language feature | Planned business rules and compliance integration |

### Something Fusion could borrow from Goose

Goose has a particularly good philosophy:

**Make memory safety a consequence of the language design, rather than something developers have to remember to do.**

Investigate applying that philosophy to Fusion's resource management.

For example, consider a service:

```fusion
service balance {
    var accountA = 1000
    var accountB = 2000

    balance.transfer {
        accountA -= 100
        accountB += 100
    }
}
```

The service owns both variables.

The runtime controls:

- Who can access the variables.
- When the service executes.
- Whether operations can run concurrently.
- How requests are scheduled.
- When the service is stopped.
- When its resources can be released.

This is different from Goose's model. Goose primarily controls memory ownership and lifetimes, whereas Fusion's proposed services also control execution and access to shared state.

## 2.7 Recommended ideas for Fusion

Do not simply copy Goose's memory model. Its restrictions could become problematic for general-purpose business applications.

Investigate combining ideas from:

1. **Goose:** Compiler-inferred ownership and safe memory lifetimes.
2. **Rust:** Strong type safety and ownership principles.
3. **C#:** Resource management and familiar application development.
4. **Java:** Interfaces, managed runtime and mature tooling concepts.
5. **Erlang:** Isolated processes and message-based concurrency.
6. **Smalltalk:** Live programming and runtime inspection.

The goal should be to make Fusion easier to use than Rust while retaining strong memory and concurrency guarantees.

## 2.8 Useful resources

- [Goose official documentation](https://aardappel.github.io/goose/) – Language reference, tutorial and examples.
- [Goose GitHub repository](https://github.com/aardappel/goose) – Compiler implementation, benchmarks and source code.

## 2.9 Overall conclusion

Goose is worth studying, especially its compiler-managed memory model. It is attempting to solve one of the hardest problems in systems programming: providing predictable performance without making developers manually manage memory or write lifetime annotations.

For Fusion, the bigger opportunity is combining that kind of compiler-enforced safety with the service-based concurrency model.

That could give Fusion a distinctive identity rather than making it another Rust or C# alternative.

---

## Research notes and caveats

- Goose is a young, evolving language. Check its current documentation and repository before relying on syntax, feature availability or compiler behaviour.
- Benchmark figures above are claims published by the Goose project. Treat them as workload-specific results, not universal performance rankings.
- Fusion is still under development. All Fusion capabilities in this document are proposed directions or design goals unless separately implemented and verified.
- The Goose syntax examples are illustrative; verify exact syntax against the current language documentation.
