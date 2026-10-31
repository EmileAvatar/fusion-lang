# Ownership: one owner, moves, borrows - and one writer

Fusion's borrow rules: who owns a value, what assigning and passing do, and how one writer is
kept when threads share a value. Taken from Rust's borrow checker, made simpler where Fusion
can be. **Status: designed, not built** - FEATURES.md Task 48 (after all of Task 32), the
thread parts Task 42. The decisions and the discussion behind them:
`Notes/Ownership_Decisions_2026-10-31.md` (D1-D49).

Related: `Object_Lifetime.md` (the counting that is built today), `files/Service.md` (the
service side), `Concurrency.md` section 3.13 (threads), `Arrays.md` (Lists and Maps),
`Classes.md`.

---

## 1. The rules (from Rust's borrow checker)

| # | Rule | In Fusion |
|---|---|---|
| R1 | **One owner** - every object, List and Map has exactly one owner at a time | a local variable, a field, a List element or a service |
| R2 | **Assigning moves** - `Car b = a` hands it over, and `a` is dead | using `a` again is a compile error, until it gets a new value |
| R3 | **Passing borrows** - `f(a)` lends `a` for the call | `a` is back afterwards; the called function's signature says read or change |
| R4 | **Many readers or one writer**, never both at the same time | readonly borrows may overlap; a changing borrow is alone |
| R5 | **A borrow never outlives its owner** - it can't be stored, returned or captured | so Fusion needs no lifetime annotations (simpler than Rust, as safe) |
| R6 | **`shared` is the written exception** - counted, read only except to the holder that made it shared | `byRef` lends the right to change it |
| R7 | **The thread boundary** - a value two or more threads use goes through one writer | a service - made automatically when needed (section 6) |
| R8 | **Copies are written** - `byVal x` | an object copies with `clone()` (Task 32.5) |

Setting: `[memory] assignment = "move"` (default) | `"share"` (today's behaviour: two names,
one object). Moving is the default on purpose - it is the only default that gives one writer
by construction (D1a).

---

## 2. Moving, borrowing, copying

```fusion
Car a = Car("red")
Car b = a                      // moved: b owns it
print(a.color)                 // error: 'a' was moved to 'b' on line 2 - use byVal a for a copy
a = Car("blue")                // fine: a has a value again

List<int> xs = [1, 2]
List<int> ys = byVal xs        // a copy: two Lists
paint(xs)                      // a borrow: xs is back after the call
Car first = fleet[0]           // a borrow: fleet can't change while 'first' is used
Car mine = fleet.removeAt(0)   // taking an element out is a move
```

#### Truth table 1: each operation, by kind of value

| Operation | int, a struct of plain values | string | List, Map, object | a struct holding a List / Map / object | `shared` object |
|---|---|---|---|---|---|
| `T b = a` | copy | copy (immutable) | **move** | **move** (all of it) | one more reader (counted) |
| `T b = byVal a` | copy | copy | copy (deep, `clone()`) | copy (deep) | a copy, not shared |
| `f(a)` | copy | copy | **borrow** - changeable unless readonly | borrow | read-only borrow |
| `f(byRef a)` | borrow, changeable | - | borrow, changeable | borrow, changeable | **lends the right to change it** |
| `f(readonly a)` (at the call) | - | - | borrow, no change | borrow, no change | read-only borrow |
| `T b = list[i]` / `T b = obj.field` | copy | copy | **local borrow** - the owner is frozen while `b` is used | local borrow | reader |
| `this.f = a`, `list.add(a)`, `return a` | copy | copy | **move** | move | one more reader |
| `a = T(...)` after a move | - | - | allowed: alive again | allowed | allowed |

#### Truth table 2: a struct holding a collection (D4)

The collection belongs to the struct. It only lends itself - moving it out would break the
struct. The same holds for every field (D.026): a struct's fields can't be moved out, only
borrowed; the whole struct moves or is borrowed. Arrays, Lists and Maps move in normal code
(D.025).

| Code | Result |
|---|---|
| `List<int> xs = order.items` | a **borrow** of the struct's List - `order` is frozen while `xs` is used |
| `xs.add(5)` on that borrow | changes `order.items` (a changing borrow) |
| `this.keep = order.items` / `return order.items` | an error: a borrow can't be stored or returned - `byVal order.items` copies it |
| `Order o2 = order` | moves the whole struct, its List with it |
| `Order o2 = byVal order` | a deep copy - two Lists |
| `order.items = other` | moves `other` into the struct (the old List is freed) |

#### Truth table 3: paths through the code

| Case | Result |
|---|---|
| moved in only one branch of an `if` | dead after the `if`, unless every branch gives it a new value |
| moved inside a loop | an error, unless the loop gives it a new value each time round |
| `a.drive()` | a borrow of `this` |
| a function value capturing a borrow | an error (R5); capturing a moved value or a copy is fine |
| a borrow alive while the owner is used | reading the owner: fine if the borrow only reads; changing it: an error |

**What it gains:** a moved object needs no count change - counting stays only for `shared`
objects and service handles (the 32.10e "proven single owner" goal, made the rule; Task
38.2 is covered by it).

---

## 3. `shared` objects (D11, D12)

```fusion
shared Car pool = Car("van")   // counted; this holder may change it
shared Car mine = pool         // one more reader
mine.color = "red"             // error: 'mine' only reads a shared Car - the holder that made it shared changes it
repaint(byRef mine)            // error as well - only the owner lends the right to change it
repaint(byRef pool)            // fine: repaint may change it
```

| Holder | Read | Change | Lend for change (`byRef`) |
|---|---|---|---|
| the holder that made it shared | yes | yes | yes |
| any other holder | yes | **no** | no |
| a function given it `byRef` by the owner | yes | yes | no (a borrow can't lend further) |

---

## 4. readonly: the caller and the called (D13-D20)

| Side | Writes | Meaning |
|---|---|---|
| **called** (the signature) | `void function show(readonly Account a)` | a promise: only reads it - checked against the body |
| **called** (the signature) | `void function log(Account a)` | borrows it, may change it, hands it back |
| **caller** (at the call) | `show(readonly acc)` | a demand: this call must not change acc |

```fusion
Account acc = Account()
show(readonly acc)        // fine: show only reads
log(readonly acc)         // error here: log changes a (logging.fusion line 12, a.lastLogged = ...)
log(byVal acc)            // fine: log changes a copy
log(acc)                  // fine: log borrows it, changes it, hands it back
```

#### Truth table 4: Bob adds `a.lastLogged = now()` to `log`

| Where `log` is | The caller writes | The caller sees | Bob sees |
|---|---|---|---|
| the same project | `log(readonly acc)` | an error at the call, naming Bob's line | **an error at his new line**, naming the readonly call |
| the same project | `log(acc)` | nothing - a changing borrow is allowed | nothing |
| a Fusion library | `log(readonly acc)` | an error: "log's signature borrows a to change it - pass byVal acc" | nothing - his signature says he may change it |
| a Fusion library | `log(acc)` | nothing | nothing |
| a library not written in Fusion (C, ...) | anything borrowed | **a warning**: nothing can be guaranteed about it - pass byVal | - |

- Inside a project, what a function does is worked out from its body through every call
  (the 32.2e check) - so the error points at the exact line that changes it
- Across a library, only its signature counts: no written or published `readonly` means
  "may change it" - never trust code; the caller is responsible
- `--interface` prints the readonly result of each public function, so a library's signature
  changes visibly when an edit changes it
- readonly also tells a service which requests are reads (section 6)

---

## 5. Send and sync, in Fusion's words (D37-D39)

- **send** - a value goes from a variable or object to another thread, and the sender no longer
  has it. Like a Go channel send, but the compiler checks it
- **sync** - a value shared by several threads through a service: only the service's thread
  changes it
- The developer never writes them; errors say "send", "copy" or "service"

#### Truth table 5: a value reaching another thread

| Value | `go f(x)`, one thread | `go f(x)`, two or more threads | `go f(readonly x)` | `go f(byVal x)` | `service(s).send(x)` (into a mailbox) |
|---|---|---|---|---|---|
| int, plain struct | copied | copied | copied | copied | copied |
| string | copied (immutable) | copied | copied | copied | copied |
| List, Map, object | borrowed - the parent frozen | **sync**: a temporary service | read in parallel, frozen meanwhile | each thread its own | **send**: moved, the sender loses it |
| a struct holding a List | borrowed | sync | read in parallel | each its own | send: moved |
| `shared` object | read only | sync: a temporary service | read in parallel | a copy | an error - send a copy (`byVal`) |
| service handle | shared (atomic count) | shared | shared | an error - a service can't be copied | the handle travels |
| a function value holding a borrow | error | error | error | - | error |

#### Fusion and Go

| | Go | Fusion |
|---|---|---|
| sending | a value or pointer down a channel - the sender **can keep using a pointer** | moved: using it after sending is a compile error |
| sharing | a mutex by hand, or a goroutine that owns the value | a service, written or made automatically |
| a data race | possible; `-race` may catch it while testing | impossible: checked by the compiler |

---

## 6. One writer: the temporary service (D21-D27)

```fusion
Account acc = Account()
go deposit(acc)           // thread 1: acc becomes service(acc), its owner; deposit borrows it
go deposit(acc)           // thread 2: its call waits in the mailbox while thread 1's runs
print(acc.balance)        // the parent's use is a request too - it waits its turn
// both threads ended: the service is gone, acc owns its value again
```

#### Truth table 6: the life of a temporary service

| Step | Owner | Who may change it |
|---|---|---|
| before the first `go` | `acc` (the parent) | the parent |
| one thread borrows it, nobody else uses it | the parent lends it; the parent is frozen until the thread ends | that thread |
| a second thread borrows it, or the parent uses it while a thread does | **`service(acc)`**, made by the compiler | its worker: one request at a time; readonly requests may overlap |
| a thread's call ends | the service; that borrow ends | - |
| the last borrowing thread ends | **`acc` again**, the service is gone | the parent |

#### Truth table 7: what the compiler makes

| Threads using it | Does any change it? | The parent uses it meanwhile? | Result |
|---|---|---|---|
| 1 | no | no | a read-only borrow, no service |
| 1 | yes | no | a borrow; the parent frozen until the thread ends |
| 1 | either | yes | a temporary service - the parent's use waits its turn |
| 2 or more | no (all readonly) | reads only | no service: readers in parallel, the value frozen meanwhile |
| 2 or more | yes | either | **a temporary service**: one writer at a time, the rest queued |
| unknown (passed to a function value) | ? | ? | an error: "make it a service yourself, or pass byVal" |

- One request = one whole call (`deposit(acc)`) - "it locks acc while thread 1 runs"
- A function that starts threads further down is followed through the calls (like readonly)
- The threads may change the data as needed - only a readonly signature or call forbids it
- Setting `[concurrency] autoService = "on"` (default: a one-line note per variable - "acc is
  used by 2 threads - made service(acc)") | `"warn"` | `"off"` (an error: write the service)
- The service is a `SharedService` (files/Service.md "The Service interface"); like every basic
  service it has one worker thread (D27)

---

## 7. Several variables: the group service (D.077)

- **Service** - manages one resource
- **Group service** - manages several resources that one thread uses
- A thread using two or more resources: they become a **group service** - written by the
  developer (`service(db, queries) shop`, 42.3), or made by the compiler when it sees the
  thread use them
- The group service is their **temporary owner**; its worker borrows them and carries out
  the requests
- When the requests are done it lets go, and each variable owns its value again

```fusion
service Database db = Database("shop.db")
service LogFile queries = LogFile("queries.log")

List<Row> function find(string sql)
    List<Row> rows = db.query(sql)      // find uses db and queries: the compiler makes
    queries.write(sql)                  // a group service of the two for this thread
    return rows                         // the results go back to the caller
```

#### Truth table 8: one thread using several resources

| Resources the thread uses | Written as | Result |
|---|---|---|
| 1 | a variable | a (temporary) service when other threads use it too (section 6) |
| 2 or more | `service(a, b) unit` | the developer's group service: it owns both while it runs |
| 2 or more | nothing written | **a group service made by the compiler** - with a note, like a temporary service |
| 2 or more, one of them only read (readonly) | either | the read one may be read in parallel |
| the group's requests done | - | it lets go; each variable owns its value again |
| a request waiting for another thread's result while it holds a service | - | **an error** (a deadlock pattern) |

No thread ever holds two separate services at once (P2), so no circle of waiting can form.

---

## 8. Questions still open

- The exact error texts (written with the first sub-task)
- How far `--interface` shows the readonly results of private functions (likely: public only)

## 9. Decisions log

| Date | Decision |
|---|---|
| 2026-10-31 | Assigning moves (default; `[memory] assignment = "share"` keeps sharing); Lists and Maps move too; `byVal` copies; passing and reading elements borrows (D1-D10) |
| 2026-10-31 | A struct's collection only lends itself - assigning it outside is a borrow (D4) |
| 2026-10-31 | A struct's fields are only borrowed, never moved out; the whole struct moves or is borrowed (D.026) |
| 2026-10-31 | Across threads: a temporary service first; `send` moves data and its ownership to another thread; or share a readonly value (D.028) |
| 2026-10-31 | `shared`: read only except to the holder that made it shared; `byRef` from it lends change (D11, D12) |
| 2026-10-31 | readonly: the called function's signature is the contract; the caller may write `readonly` at the call; a library only by its signature; a non-Fusion library: a warning (D13-D20) |
| 2026-10-31 | Two or more threads using a value: a temporary service owns it, the threads borrow, ownership comes back when they end (D21-D27) |
| 2026-10-31 | Several resources used by one thread: a group service, written or made by the compiler; it owns them while it runs, then each variable owns its value again (D.077 - replaces the fixed order) |
| 2026-10-31 | Send / sync worked out by the compiler, explained in Fusion's words (D37-D39) |
