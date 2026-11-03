---
name: fusion-ownership
description: Fusion's ownership, borrowing, readonly and const rules - what moves, what is copied, what is borrowed, what is allowed and what is an error, with the decision behind each. Use before designing, building, testing or reviewing anything about moving, borrowing, byVal / byRef / readonly, getters, const / let, or [memory] settings in the Fusion compiler (Task 48, Task 50), and when writing Fusion code that hands objects, Lists or Maps around.
---

# Fusion ownership rules

The rules as they stand. The full design and truth tables are in `Ownership.md`, every rule as
code (allowed / not allowed, [built] / [designed]) in `files/showcase/Ownership.fusion`, the
decisions in `Decisions.md`. **Keep these four in step**: a rule changed in one is changed in
all, in the same session (Rule 3b), with a test for each allowed and not-allowed case (Rule 4c).

Before proposing a change, grep `Decisions.md` for the subject; if it goes against an ACTIVE
decision, tell the user first.

## Settings (`[memory]` in fusion.toml)

- `assignment = "move"` - the default since 48.9 (D.102). `"share"`: two names, one object
  (today's counting) - kept for projects and tests of it; the self-hosted compiler uses it
  until Task 35 (`selfhost/fusion.toml`, D.107)
- `moveFieldOut = false` (D.108) - true: a field may leave a struct the function owns, as in
  Rust; the struct can't be used until it gets a new value

## What moves, what is copied

| Kind | Handed over |
|---|---|
| List, Map, class object, interface value, a struct holding one of them | **moves** (a struct as a whole - D.097) |
| int, float, bool, char, byte, string, a struct of plain values | copied |

Handed over = `T b = a`, `b = a`, `x.f = a`, `list.add(a)` / `insert`, `m[k] = a`, `[a, b]`,
`Order(1, xs)`, `return a`, and a call to a function that keeps that parameter.

## Allowed / not allowed - built

| Code | Result | Decision |
|---|---|---|
| `Car b = a`, then `a.color` | error: 'a' was moved to 'b' on line N | D.014 |
| `a = Car(...)` after a move | ok - a is back | 48.1 |
| moved in one branch / in a loop without a new value each pass | error (maybe moved / earlier pass) | 48.1 |
| `Car b = byVal a` | ok - a deep copy; a struct's objects cloned too | D.097 |
| `f(a)` | ok - lent for the call, a is back after | R3 |
| `f(a)` where f stores, adds or returns its parameter | moves a (f takes it) | D.100 |
| `car.paint()` where paint keeps `this` | never moves car - `this` is always borrowed | D.103 |
| `Car c = fleet[0]` / `order.items` / `for c in fleet` | a local borrow; the owner frozen until the borrow's last use | D.101 |
| change the owner while the borrow is used | error: 'fleet' can't change while 'c' borrows from it | D.101 |
| read the owner while the borrow changes it | error (one writer or many readers) | R4 |
| store or return a borrow (`g.car = c`, `list.add(c)`) | error - `byVal c` copies | R5 |
| `return order.items` / `list.add(fleet[0])` of a value the function owns | error - a field / element can't be moved out | D.026 |
| a method returning its own field / element (`return this.engine`) | ok - the result lends from the object | D.109 |
| a function returning a part of a parameter it borrows | ok - lends from that argument | D.109 |
| returning a new object made with a part of `this` (an iterator) | ok - lends from `this` | D.109 |
| a single object the function made, returned | moves to the caller | D.111 |
| `Engine e = car.getEngine()` | e borrows from car - changes reach car; car frozen while e used | D.109 |
| `list.add(car.getEngine())` | error - `byVal` for a copy | D.109 |
| `for x in xs` and `xs.add(..)` inside | error (D.058, every mode) | D.058 |
| `for x in xs` and `xs[0] = x` (int elements) | ok - a value set (27.2e); with object elements: error | 27.2e |
| `f(readonly a)` where f changes / keeps it | error at the call and at the changing line | 48.3 |
| `f(readonly n)` with an int / string | error - copied anyway | 48.3 |
| `f(byRef a)` / `f(readonly a)` where f keeps it | error - only lends | 48.3 |
| `Car b = byRef a` | ok - a local borrow of a | 48.3 |
| `g.car = byRef a` | error - a borrow can't be stored | 48.3 |
| `byRef` on a plain struct | error - waits for [structs] allowReference | 32.10a |
| `readonly Car c` parameter: change, keep, pass to a changer, give to a function value | error - deep, followed through calls | D.011 |
| `readonly byVal Car c` | error - readonly stands alone | 32.2e |
| `Circle c = (Circle)s` | moves s; `byRef (Circle)s` borrows, `byVal` copies | D.104 |
| `let c = ...; c = other` | error; `c.field = ..` ok | SYN.008 |
| `const` List / Map / struct: change | error (deep) | - |
| `const Car k`: `k = ..` | error | - |
| a match `case X(name)` | `name` is a new variable for that case | 48.9 |

## Designed, not built (Task 50 - after Task 48)

- **A readonly result** (D.110): `public readonly Engine function getEngine()` - part of the
  signature; the caller gets a read-only borrow. No `readonly` in that function's body
  (`return readonly x` is an error). `byRef` on its result: error. `byVal`: a changeable copy.
  What it may return besides a member: decided while building (user)
- **const deep on an object** (D.112): `const Car k`, then `k.color = ..` or `k.paint()` - an
  error (today allowed); a `byVal` copy may change

## Postponed / rejected

- `shared` - postponed until a real need; `byRef` shares an object meanwhile (D.106)
- `Unique<T>`, `.move()` - rejected: assigning moves (D.080)
- Taking an element out as a move - needs a `removeAt` that returns it (48.2 -> Task 33)
- A function value can't capture a borrow - built, waits for closures

## Where it lives in the compiler

- `src/semantic/ownership.py` - moves, borrows, freezing, kept / lent parameters (fixed point
  across functions); runs when assignment = "move"
- `src/semantic/readonly.py` - readonly parameters, `check_readonly_calls` (readonly at the
  call), `changed_parameters` (shared with ownership.py)
- `src/codegen/c_memory.py` - `clone_code` (byVal), struct `fusion_clone_` helpers
- Tests: `tests/test_ownership_moves.py`, `test_ownership_borrows.py`,
  `test_ownership_at_the_call.py`, `test_readonly.py`; a test of "share" itself carries
  `@pytest.mark.share` (tests/conftest.py)

## Lessons from building it

- Measure a rule change with every error "move" adds over "share" - not only messages
  containing "moved" (borrow errors were missed once)
- Restore a file changed for a measurement with a targeted replace, never `git checkout`
  (it also throws away uncommitted work)
- Write edits as Python script files, not shell heredocs (they turn `\n` into real newlines)
