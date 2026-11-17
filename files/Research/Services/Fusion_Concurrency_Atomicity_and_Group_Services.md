# Fusion Concurrency: CPU Interruptions, Atomic Operations and Services

**Purpose:** Explain why a CPU can pause a thread even while it is performing a critical operation, how locks protect that operation, and how Fusion services provide the same protection through ownership and request execution.

**Source of truth:** This note follows the terminology and design in `Service.md`. It is an explanatory companion, not a replacement for that specification.

## 1. The CPU can interrupt a thread at almost any point

A CPU core executes instructions for a scheduled thread. The operating system can pause that thread and schedule another one.

Common reasons include:

- Its time slice expires and the scheduler selects another runnable thread.
- The thread waits for a lock, I/O, a timer or another event.
- A hardware interrupt requires operating-system attention.
- A page fault requires memory-management work.

When a thread is paused, the system preserves its execution state so it can resume later. The thread does not restart from the beginning.

**Important:** A CPU interruption does not automatically make shared data safe. Another thread may run while the first thread is paused.

## 2. Why the balance example needs an atomic operation

Assume the account balance is `1000`, and two threads each try to withdraw `500`.

```fusion
if balance > 500 {
    balance = balance - 500
}
```

The condition and update are multiple logical steps:

1. Read the balance.
2. Compare it with `500`.
3. Decide whether the withdrawal is allowed.
4. Calculate the new balance.
5. Write the new balance.

A possible interleaving is:

| Order | Thread A | Thread B | Balance |
|---:|---|---|---:|
| 1 | Reads `1000`; condition is true | | 1000 |
| 2 | Gets paused | | 1000 |
| 3 | | Reads `1000`; condition is true | 1000 |
| 4 | | Subtracts `500` and writes | 500 |
| 5 | Resumes using its earlier decision | | 500 |
| 6 | Subtracts `500` and writes | | 0 |

Both threads passed the check using the old balance. This is a **race condition**. The problem is that the check and update were not one indivisible operation.

## 3. A lock protects the whole critical section

A conventional lock makes the whole check-and-update exclusive:

```text
lock(balanceLock) {
    if balance > 500 {
        balance = balance - 500
    }
}
```

If Thread A owns the lock and is interrupted, Thread B may still be scheduled. But when B tries to acquire the same lock, it must wait. It cannot enter the protected section until A releases the lock.

The lock does **not** stop the CPU from interrupting A. It prevents B from entering the same protected critical section at the same time.

While B waits, the operating system can run other runnable threads.

## 4. Fusion: one service request is an indivisible step

Fusion's service design uses ownership and request execution rather than requiring every caller to manage a lock around shared state.

The balance operation is written as one service operation (the form in `Service.md`):

```fusion
service(balance).run {
    if balance > 500 {
        balance = balance - 500
    }
}
```

A shorter `balance.run { ... }` is not in the spec. The point: **the check and deduction belong to one atomic service operation.**

What happens:

1. A thread submits the operation to the balance service.
2. The service executes the complete block as one operation.
3. A competing request cannot interleave a conflicting change to that service's state.
4. When the operation finishes, the next request can be processed.

The service worker can still be interrupted by the operating system halfway through the block. That is safe: the next conflicting request does not execute against the same service state until the current operation has finished.

## 5. Group services: one owner for multiple variables

A group service puts two or more variables under **one service owner**. The group service owns/manages the grouped data while the group exists; the member variables are not independently owned by separate services during that time.

For example:

```fusion
service(account, ledger) accountService
```

After grouping:

- `accountService` is the one service responsible for requests involving `account` and `ledger`.
- Access to either member is routed through the group's request queue.
- An operation can work with `account`, with `ledger`, or with both.
- A multi-variable operation can be executed as one atomic group operation.
- Other threads cannot bypass the group and directly mutate a member.
- A variable may belong to at most one service or group at a time - putting it in a second one is a compile error (group rule 4).
- Nesting is allowed: a group may contain another group, as long as no variable gets two owners (group rule 5).

Example of a coordinated operation:

```fusion
service(accountService).run {
    if account.balance >= 500 {
        account.balance -= 500
        ledger.recordWithdrawal(account.id, 500)
    }
}
```

The important point is that the **group service owns the coordinated operation**, not that `account` and `ledger` each get separate locks. The operation can safely read or update one member or several members together.

According to `Service.md`, when the group goes out of scope, its members are released from the group and ownership returns to the variables under the documented ownership rules.

## 6. CPU atomic instructions versus a service operation

These are related but different levels of atomicity:

| Mechanism | What it makes indivisible |
|---|---|
| CPU atomic instruction | One supported machine-level read/modify/write operation, such as an atomic increment or compare-and-swap. |
| Lock | A programmer-defined critical section protected by the same lock. |
| Fusion service operation | A request/operation executed under the service's ownership and serialization rules. |
| Fusion group service operation | An operation involving one or more grouped members, executed as one coordinated step. |

A simple integer operation may be implemented by Fusion using CPU atomic instructions, as described in `Service.md`. But a conditional operation such as “if balance is sufficient, then deduct and record the withdrawal” is a multi-step operation. It needs the service's atomic operation/group semantics, not merely an atomic subtraction.

## 7. Key rules for Fusion

- **The CPU may pause a service worker.** Atomic service execution does not mean the worker is uninterruptible.
- **Conflicting requests do not interleave.** The service controls access to its owned state.
- **A service is not re-entrant.** It finishes one request before starting the next (Service.md rule 3), so a request that waits on its own service deadlocks.
- **One owner controls mutation.** The worker is the only writer; internal mutable references must not escape.
- **A group is one owner for multiple variables.** Its operation may work on A, B, or both as one step.
- **The service is not a universal CPU lock.** It protects only the state and operations routed through that service/group.
- **Keep operations appropriately sized.** A long-running service operation can delay later requests in that service's queue.

For the complete rules, settings, group-service lifecycle and ownership requirements, see `Service.md`, especially “The five rules”, “Group services (units)” and “Ownership in a service”.
