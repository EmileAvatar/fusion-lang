# Fusion: Service Isolation, Resilience and Failure Containment

**Research for Task 42** (files/FEATURES.md "Research", 42.00): every section and list here is reviewed
when the services task starts; the findings go into files/Research/Services/, then each point is
decided. Sources: the Microsoft 365 outage report of 12-13 Nov 2026 (cybersecuritynews.com/microsoft-outage-incident-report/)
and the user's notes - Notes/MicrosoftDown example.md (not in git). Written by ChatGPT with limited
knowledge of Fusion; section 14 checks it against Fusion's design.

**Purpose:** Design-review input for Claude Code. This document captures recommendations discussed after reviewing a reported Microsoft 365 gateway outage and a Windows Explorer CD/DVD hang.

**Status:** This is a proposal/review document, not an instruction to overwrite existing Fusion specifications. Preserve agreed designs. In particular, `Timeout`, `WhenFull`, `Priority`, worker types, mailbox capacity, readers, retry and shutdown controls are already planned in the service design. Do not duplicate them. Inspect the current specifications and extend only genuine gaps.

## 1. Executive summary

Fusion's ownership and service model is a strong foundation for safer concurrency:

- A service owns its internal state.
- Other threads interact through requests rather than directly sharing mutable references.
- State-changing operations are serialized by the service.
- Read-only operations may run in parallel where safe.
- Ownership and scope determine resource lifetime.
- Mailbox limits, timeouts, priorities, worker strategies and lifecycle controls are already planned.

The recommendations here focus on resilience when operations block, resources become unhealthy, queues overload, or recovery actions create additional load.

The central design principle is:

> **Ownership isolation + execution isolation + failure isolation.**

1. **Ownership isolation:** shared mutable state has one owner; callers cannot bypass the service and mutate its internals.
2. **Execution isolation:** blocking or slow work does not block the caller or unrelated services.
3. **Failure isolation:** one overloaded, blocked or failing resource does not cascade into unrelated resources or the entire application.

A service can help contain failures, but it cannot repair a defect inside an operating-system kernel, device driver or external system.

## 2. Lessons from the Microsoft 365 gateway incident

The article supplied for this discussion reported a Windows networking gateway issue involving lock contention under a particular combination of traffic and deployment conditions. Its account included shared gateway capacity, some capacity already unavailable, CPU/memory exhaustion, automated traffic recovery increasing pressure, widespread server unresponsiveness, and gradual recovery after reverting connection handling and restarting/draining servers.

These are the article's reported claims, not an independent forensic finding by this document.

### 2.1 How Fusion services could help

If the contested shared state is application-level state controlled by Fusion, routing access through a service can replace many competing writers and manually coordinated locks with one clear owner and a request queue.

**Direct shared-state approach**

```text
Thread A ─┐
Thread B ─┼── shared mutable state + locks
Thread C ─┘
```

**Service-owned approach**

```text
Thread A ─┐
Thread B ─┼──> Service mailbox ──> Service owner/worker ──> State
Thread C ─┘
```

Potential benefits:

- One owner controls mutations.
- Requests can be processed in a defined order.
- Callers do not directly access internal mutable state.
- Compiler/runtime rules can enforce service access.
- Queue limits and admission behaviour apply before work is accepted.
- Safe read-only requests can use the existing parallel-reader model.

### 2.2 What this does not automatically solve

A service is not a magic replacement for every lock or concurrency problem.

- If a service receives more work than it can process, its queue can fill or requests can wait.
- A slow request can delay later requests in a serial queue (head-of-line blocking).
- A worker can itself become blocked.
- A service cannot remove a lock inside an operating-system kernel or third-party driver.
- A central service can become a new bottleneck and a larger failure domain.
- Instantly redirecting all work to another service during recovery can overload it.

The design should therefore make backpressure, execution boundaries and failure containment explicit.

## 3. Lessons from a Windows Explorer CD/DVD hang

Clicking a CD/DVD drive in Explorer can cause Explorer to stop responding. One possible cause is a device/driver operation running synchronously on the UI thread. If the device, driver or operating-system call takes too long or never returns, the UI thread cannot process input or repaint messages.

### 3.1 Fusion service approach

Device operations should not run on the UI thread. The UI should submit a request to a device service and remain responsive while a worker handles the operation.

Illustrative pseudocode only; use syntax already defined by Fusion:

```fusion
service CDDrive dvd = CDDrive("D:")

async dvd.readInformation()
```

Expected flow:

1. UI submits a request.
2. Request enters the service mailbox subject to its configured policy.
3. A worker performs the device operation.
4. UI continues processing input.
5. Result or error is delivered when available.
6. Caller timeout can stop the caller waiting according to existing semantics.

### 3.2 Critical limitation: timeout is not cancellation

If a driver call is blocked inside the operating system:

- The caller may stop waiting.
- The worker may remain blocked.
- The request may still complete later, fail later, or never return.
- A timeout must not be treated as proof that the worker is free.

Where possible, use OS APIs that support genuine asynchronous I/O or cancellation. Where cancellation is unsupported, treat the operation as potentially still running after the caller's timeout.

### 3.3 Isolate potentially blocking devices

A blocked CD/DVD operation should not consume a worker needed by unrelated services.

Evaluate:

- Dedicated worker or bounded worker group for the device.
- Separate resource-specific service instances.
- A supervisor/watchdog that observes operation duration and service health.
- An unhealthy/degraded state when a worker stops making progress.
- Controlled recovery, such as closing/reopening a resource where supported.
- Process isolation for especially unreliable native drivers or external components, where platform and use case justify the overhead.

Do not create an unlimited dedicated thread for every resource. Prefer bounded, configurable execution capacity.

## 4. Three isolation principles

### 4.1 Ownership isolation

A service is the only authority that can mutate its owned internal state.

- Internal references must not escape the service.
- Callers interact through requests and returned values.
- Borrowed request data is valid only for the request lifetime.
- Data moved into a service becomes owned according to existing ownership rules.
- Returned values follow existing copy/ownership-transfer rules.
- Group services coordinate multiple resources without exposing their internals.

This reinforces existing service ownership rules; it must not create a second ownership system.

### 4.2 Execution isolation

Slow or blocking work should not unexpectedly block the caller or unrelated work.

- UI threads should not perform potentially blocking resource operations directly.
- Blocking work should run on an appropriate worker.
- A blocked resource should not exhaust a general-purpose shared worker pool.
- Worker capacity must be bounded.
- Compiler/runtime should make blocking behaviour visible where it can be known.
- Consider API metadata, annotations, effects or resource declarations for operations that may block.

Potential classifications to investigate (proposal only; no syntax assumed):

- `blocking`
- `async`
- `cancellable`
- `nonblocking`

Do not assume the compiler can infer all blocking behaviour. Native calls, drivers and external libraries may block in ways it cannot prove.

### 4.3 Failure isolation

One failed or overloaded service should not bring down unrelated services.

- Bound accepted work per service.
- Apply backpressure instead of allowing unlimited queue growth.
- Keep independent resources in independent failure domains where appropriate.
- Avoid one global service becoming a bottleneck.
- Make service health observable.
- Recover gradually rather than instantly redirecting all work to remaining capacity.
- Prevent retries and recovery actions from amplifying an outage.

This complements existing mailbox, `WhenFull`, priority, timeout, worker-type and lifecycle configuration.

## 5. Existing features to reuse — do not duplicate

Inspect `Service.md`, `Concurrency.md`, `Ownership.md` and related decisions first.

| Existing planned feature | Resilience relevance |
|---|---|
| `Mailbox` | Bounds queued requests. |
| `WhenFull = WAIT / ERROR` | Defines behaviour when mailbox is full. |
| `Timeout` | Limits caller wait; does not necessarily cancel underlying work. |
| `Priority` | Schedules more important work according to scheduler rules. |
| `WorkerThreadType = AUTO / SINGLE / SHARED` | Controls worker allocation/isolation strategy. |
| `Scheduler` | Immediate, batched or custom request scheduling. |
| `Readers = PARALLEL / SERIAL` | Allows safe parallel reads while preserving serialized writes. |
| `OnError` | Error handling policy. |
| `RestartLimit` | Limits restart attempts. |
| `Retry` | Retry behaviour. |
| `IdleTimeout` | Releases idle worker resources. |
| `Shutdown` | Service shutdown behaviour. |
| `Trace` / `Name` | Diagnostics and service identification. |
| `ThreadPool` | Worker-pool selection/configuration. |
| `Affinity` | Worker affinity where supported. |
| `MemoryLimit` | Service memory limit. |
| `Access` | Service access control. |
| `Coalesce`, `BatchSize`, `BatchDelay` | Reduce redundant or excessive work where appropriate. |

Semantic details to preserve/clarify:

- A timeout is not proof of cancellation.
- `WAIT` must not imply an unlimited queue.
- Priority does not automatically guarantee fairness; define starvation behaviour in the scheduler specification.
- Retry must account for operations whose outcome is unknown.

## 6. Recommendations to evaluate and potentially add

Some may already be partly covered. Check first, then extend only where a real gap exists.

### 6.1 Explicit service health

Consider making health observable. Possible conceptual states:

- `STARTING`
- `HEALTHY`
- `BUSY`
- `DEGRADED`
- `UNRESPONSIVE`
- `STOPPING`
- `STOPPED`
- `FAILED`

Questions:

- Which states are runtime-internal versus visible to application code?
- How is unresponsiveness detected: worker progress, request age, heartbeat, queue depth or explicit health check?
- Can a degraded service recover without being destroyed and recreated?
- Can the existing `Service<T>.state` represent these conditions?

Prefer extending existing `state` if suitable rather than creating a duplicate health API.

### 6.2 Watchdog / progress monitoring

Evaluate a watchdog or supervisor for potentially blocking services. It could:

- Observe request execution duration.
- Detect workers that stop making progress.
- Record long-running requests.
- Mark a service degraded or unresponsive.
- Stop admitting new work when unhealthy.
- Trigger a configured recovery policy.

A watchdog cannot safely terminate arbitrary blocked native code. Detection and containment are not the same as cancellation.

### 6.3 Circuit breaker / admission control

Consider a circuit-breaker-like policy:

- **Closed:** admit requests normally.
- **Open:** reject new requests quickly or return a controlled unavailable result.
- **Half-open:** allow a limited number of test requests to check recovery.

Review whether this belongs in the runtime or a library. Define its interaction with existing `WhenFull`, `Timeout`, `Retry`, `OnError` and `Rule`. Avoid duplicate controls if existing mechanisms cover the same need.

### 6.4 Retry backoff and retry storms

Review existing `Retry` for:

- Exponential backoff.
- Optional random jitter to prevent synchronized retries.
- Maximum attempts or total retry duration.
- Retrying only errors classified as transient.
- Avoiding automatic retries for operations unsafe to repeat.
- Distinguishing retrying admission from retrying an operation whose outcome is unknown.

An operation may have completed even if the caller timed out before receiving its result. Retrying a non-idempotent operation can duplicate effects. Do not silently assume retries are safe.

### 6.5 Queue age and overload diagnostics

Mailbox capacity is already planned. Consider exposing diagnostic information:

- Current queue depth and configured capacity.
- Age of the oldest queued request.
- Active request count and waiting caller count.
- Completed, failed, timed-out and cancelled request counts.
- Worker utilization/progress.
- Requests rejected because the mailbox was full.

These may belong in tracing/diagnostic APIs rather than ordinary application-level service state.

### 6.6 Bulkheads and service partitioning

Keep unrelated workloads separate where appropriate.

Examples:

- A CD/DVD service should not share a worker that can be permanently blocked by another device.
- A database service should not starve a UI-critical service.
- Separate customer/tenant/workload partitions may prevent one high-volume customer consuming all capacity.
- Independent service instances can provide separate queues and worker limits.

Avoid one global service for unrelated resources. Also avoid a separate thread for every tiny operation. Aim for bounded isolation with sensible defaults.

### 6.7 Controlled recovery and load shedding

When a service or cluster is unhealthy:

- Stop or limit admission of low-priority work.
- Preserve capacity for essential work where possible.
- Do not instantly move all traffic to one remaining worker/service.
- Recover gradually.
- Apply backpressure while capacity is restored.
- Prevent retry loops from multiplying load.
- Make recovery policy observable and configurable.

A local service can enforce local limits; cluster-wide load distribution requires coordination beyond one service instance.

### 6.8 Safe shutdown and in-flight requests

Ownership scope exit and service shutdown must be coordinated.

Resolve:

- What happens when the owning scope exits with queued requests?
- Are queued requests rejected, drained or cancelled?
- What happens to an active request?
- Can a resource be destroyed while a worker is still using it?
- Does shutdown wait for a grace period?
- What happens if the active operation cannot be cancelled?
- When is ownership finally released?

**Required safety property:** An owned resource must not be destroyed while an in-flight operation can still access it.

Integrate this with existing ownership and `Shutdown` rules. Do not free memory or close a resource underneath a running worker.

## 7. Resource services: possible expansion

The current `fusion.toml` proposal already includes:

```toml
[concurrency]
resourceAsService = true
```

The existing documented resource categories include files, sockets, pipes and databases.

Consider whether to extend this model to:

- CD/DVD drives and other storage devices.
- USB devices.
- Serial ports.
- Printers.
- Cameras and capture devices.
- Audio devices.
- Network adapters or other device APIs where the platform permits.

These are proposals, not currently agreed resource categories. The test should be whether a resource has stateful operations, blocking behaviour, concurrency hazards or a lifetime that benefits from one owner. Do not turn every small value or every function call into a service.

## 8. Bottlenecks, head-of-line blocking and deadlocks

### 8.1 Head-of-line blocking

If a service executes requests serially and one request takes a long time, later requests may wait.

Possible mitigations:

- Keep service requests short.
- Split long operations into stages where safe.
- Use separate services for independent resources/workloads.
- Use parallel readers where supported.
- Do not hold a service execution slot while waiting for unrelated external work.

Do not split an operation if that breaks required service/group atomicity.

### 8.2 Nested service waits

Preserve the existing rule prohibiting a request from waiting inside one service request for another thread's result.

Example of a dangerous dependency:

```text
Service A request
    waits synchronously for Service B
        while Service B needs progress from A
```

Use asynchronous continuation/orchestration outside the service request, or a group service when multiple resources must be coordinated atomically under the existing group-service rules.

### 8.3 Avoid a central bottleneck

Do not route all application activity through one universal service. One resource should have its own service; a group service coordinates resources that genuinely require coordinated operations. Independent workloads should remain independent.

## 9. Suggested test scenarios

These are test ideas, not claims that the runtime currently supports every behaviour.

1. **Slow device:** A device request takes several seconds; the UI thread remains responsive.
2. **Never-returning device call:** Caller times out, worker remains blocked, unrelated services continue.
3. **Mailbox full:** `WAIT` and `ERROR` behave according to specification.
4. **Priority under load:** High-priority requests receive the specified treatment without accidental starvation.
5. **Read/write concurrency:** Safe reads execute in parallel; writes remain serialized.
6. **Worker-pool saturation:** A blocked resource cannot consume all workers required by unrelated services.
7. **Retry storm:** Transient failures do not cause synchronized overload.
8. **Unknown operation outcome:** A timed-out non-idempotent operation is not silently duplicated.
9. **Service shutdown:** Scope exits with queued/active requests; no resource is destroyed while still in use.
10. **Service failure:** A failed service does not corrupt or stop unrelated services.
11. **Recovery surge:** Admission and recovery remain gradual and bounded.
12. **Group service:** Multi-resource operations remain atomic and obey the no-nested-wait rule.
13. **Memory pressure:** Service memory limits and mailbox capacity interact predictably.
14. **Observability:** Queue depth, request age, worker progress and failures can be diagnosed.

## 10. Design review checklist

For each item, classify it as **Already specified**, **Partially specified**, **Not specified**, or **Not suitable**. Cite the exact existing document/section.

| Review item | Suggested direction |
|---|---|
| Service health | Reuse/extend existing `state` if appropriate. |
| Watchdog/progress detection | Evaluate for blocking services; do not promise arbitrary thread termination. |
| Circuit breaker | Evaluate as admission control; avoid duplicating `Rule`/`OnError`. |
| Retry backoff/jitter | Check existing `Retry`; clarify idempotency and unknown outcomes. |
| Queue diagnostics | Consider queue depth, oldest request age and worker progress. |
| Bulkhead isolation | Clarify how `SINGLE`, `SHARED`, `AUTO` and `ThreadPool` isolate blocked work. |
| Load shedding/recovery | Define gradual recovery and admission control, especially for distributed workloads. |
| In-flight shutdown | Ensure ownership release waits until active operations no longer use the resource. |
| Blocking API classification | Explore annotations/effects or resource metadata; do not assume perfect inference. |
| Device resource coverage | Evaluate adding devices to `resourceAsService`; do not silently change the current list. |

## 11. Implementation constraints

1. **Do not replace ownership with garbage collection.** Fusion intends deterministic ownership/destruction when the owner leaves scope, subject to safe in-flight use.
2. **Do not bypass service ownership.** No external mutable reference to service-internal state.
3. **Do not duplicate existing settings.** Timeouts, `WhenFull`, priorities, worker types, readers, retry, shutdown and related controls are already planned.
4. **Do not claim timeout means cancellation.**
5. **Do not claim a watchdog can safely kill arbitrary blocked native/kernel operations.**
6. **Do not create unbounded threads or queues.**
7. **Do not centralize unrelated resources into one service.**
8. **Preserve atomicity.** Do not split service/group operations in a way that violates their guarantees.
9. **Preserve the existing nested-wait/deadlock rule.**
10. **Keep proposals separate from agreed decisions** until explicitly accepted.

## 12. Task for Claude Code

Use this document as a design-review checklist, not as permission to implement every proposal immediately.

1. Read the current `Service.md`, `Ownership.md`, `Concurrency.md`, `Concurrency_Traps.md`, `fusion.toml` design and relevant decision notes.
2. Locate existing definitions for `Mailbox`, `WhenFull`, `Timeout`, `Priority`, `WorkerThreadType`, `Readers`, `Retry`, `OnError`, `Shutdown`, `state`, `ThreadPool` and service ownership/lifetime.
3. Build a gap analysis against Sections 4–10.
4. For each recommendation, identify whether it is already covered, partially covered, missing or unsuitable.
5. Do not rewrite existing specifications wholesale. Propose the smallest coherent changes in the appropriate documents.
6. Keep existing syntax and terminology unless a change is explicitly proposed.
7. Do not mark a proposal as an agreed Fusion feature without approval.
8. Add/update implementation tasks only after design changes have been reviewed and accepted.
9. Ensure tests cover the failure cases in Section 9.
10. Report what already existed, what needs clarification, proposed new features, trade-offs and which specification files would change.

**Expected output from Claude Code:** a concise gap-analysis report and targeted proposed specification edits. Do not silently implement speculative features.

## 13. Final architectural position

Fusion services can provide a useful foundation for resilient concurrent software by combining controlled ownership, serialized mutation, queued requests and configurable execution.

The strongest design is not simply "put everything in a service." It is:

- Give mutable state one owner.
- Keep blocking work away from caller/UI threads.
- Bound queues and worker capacity.
- Isolate resources that can block or fail independently.
- Make overload and service health observable.
- Recover gradually and avoid retry amplification.
- Keep ownership valid until all in-flight work has stopped using the resource.

This can reduce application-level races, lock contention, UI freezes and cascading failures. It cannot guarantee that a defective operating-system kernel, driver or external service will behave correctly. Fusion's responsibility is to make the boundary explicit and contain failures wherever the runtime has control.

---

## 14. Gap analysis against Fusion's design (Claude, 2026-11-16)

Checked against files/Service.md, files/Concurrency.md and files/Concurrency_Traps.md. Proposals only -
nothing here is a decision or a task until the user accepts it.

#### Already specified
- **Timeout is not cancellation** - Service.md rule 5: every request ends completed, failed, timed out
  ("its effects may still happen") or cancelled
- **Bounded queue** - `Mailbox` (default 12), `WhenFull` WAIT / ERROR (`QueueFullError`), `WarnAt` (80%)
- **No starvation by priority** - `Priority` is shares of the turns ("5.4.1"), not strict priority
  (Concurrency.md "Priority": strict priority starves - trap 6)
- **A device on its own workers** - `WorkerThreadType.SINGLE` "suits a heavy resource that should never
  wait for a free worker, such as ... a device" (Service.md WorkerThreadType); `ThreadPool` per service
- **Owned threads** - every thread has a parent that waits for, cancels and gets errors from its children
  (Concurrency_Traps.md P5)
- **Restart limits** - `OnError` (restart / stop / report), `RestartLimit` (Service.md secondary settings)

#### Partly specified - a gap to close
- **Health** - `ServiceState function state()` is in the Service interface (Service.md) but its states
  are not listed: STARTING, HEALTHY, BUSY, DEGRADED, UNRESPONSIVE, STOPPING, STOPPED, FAILED
- **Watchdog** - only hot-path services have one (Service.md T7); an ordinary service has none - e.g. a
  `Watchdog = 10s` setting: a request running longer marks the service UNRESPONSIVE (it detects, it
  never kills a blocked native call)
- **Retry** - listed (Service.md) with no detail: attempts, backoff with jitter (Concurrency.md has
  backoff with jitter only for livelock), only errors marked transient, never automatically for a
  timed-out request whose effects may still happen
- **Diagnostics** - `waiting()` gives the queue length and `Trace` profiles; missing: the oldest
  request's age, completed / failed / timed-out / rejected counts, worker progress - the user's
  dashboard idea (below) needs exactly these
- **Shutdown and requests still running** - `Shutdown` (finish the queue or drop it) and `final`
  exist, and a drain step for hot paths (T8); missing the safety rule: the owner's scope can't free
  a resource while a request is still using it - and what happens when that request never returns
- **AUTO and blocking work** - `AUTO` may move a resource to `SHARED`; a resource that can block
  (a device) must never land on a shared pool, or it can take the pool's workers with it
- **Resources as services** - `resourceAsService` covers files, sockets, pipes and databases; devices
  (CD/DVD, USB, serial ports, printers, cameras, audio) are not listed

#### Not specified
- **Recovering gradually** - after a restart, admit work slowly (a ramp-up), not the whole waiting queue
  at once; shed low-priority work while DEGRADED
- **Circuit breaker** - closed / open / half-open admission; probably a library (a Resilience module)
  using `WhenFull`, `Timeout` and `OnError`, not new core settings
- **Marking blocking calls** - a `blocking` mark on functions and native calls, so the compiler can
  refuse one on a UI thread or a hot path (as hot paths already refuse unknown calls - Service.md H4)

#### The user's dashboard idea (Notes/MicrosoftDown example.md - the incident report and the user's notes; not in git)
- Designed later, once a GUI and services work: the dashboard plugs into whatever GUI or service the
  developer uses (user, 2026-11-16)
- The thread pools and services report their state to a dashboard; admins see a constrained resource
  and change its `Timeout` or `ThreadPool` size
- Needs the diagnostics above, and a rule for who may change settings while running: today only the
  thread that created a service may (Service.md "Using a service") - an admin channel would be a new,
  checked way in

#### Could Fusion have prevented these two cases?
- **The Microsoft 365 outage** - its root was lock contention inside a Windows process, which Fusion
  can't fix. What made it global could be contained: the automatic recovery moving all connections to
  the healthy servers (gradual recovery, admission), the fault boundaries that failed (bulkheads - one
  service per region or tenant), restarted servers failing again when the waiting traffic returned
  (ramp-up)
- **The CD/DVD hang in Explorer** - yes, at the application's level: the UI never calls the drive
  itself, a `SINGLE` drive service does; the UI's timeout lets it carry on. The blocked worker may stay
  blocked (the OS call can't be cancelled), but only the drive's service is stuck

#### Suggested next steps (for the user to accept)
1. ServiceState's values and how each is detected
2. A `Watchdog` setting for ordinary services
3. `Retry` in detail (attempts, backoff, jitter, transient errors only, never after a timeout)
4. Diagnostics for a service and a pool (counts, oldest request, progress) - the dashboard's data
5. The shutdown safety rule (no resource freed under a running request)
6. Devices in `resourceAsService`; blocking resources never on a shared pool
7. Later: gradual recovery, a circuit breaker module, a `blocking` mark
