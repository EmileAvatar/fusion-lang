# Fusion - Open Questions

Questions not decided yet. Next to `Decisions.md`: when the user answers one, the answer goes
into `Decisions.md` (and the design document named) and the question is removed here. A new
question gets the next number (never reused). Claude adds a question here instead of guessing
(CLAUDE.md Rule 3b).

**How a question is written (user, 2026-11-07):**
- A heading `#### Q.NNN` with a short title and where it belongs (task, document)
- One or two lines: the question
- **An example code block** wherever code can show it - Claude's understanding of today's
  rule and the options, marked `A:` / `B:` / `C:`, so the user can see it and answer by letter.
  Only a question code can't show (a review, a name) goes without one
- Claude's suggestion, if it has one, marked "suggested"

Ideas not scheduled yet keep their own open questions in `files/FutureFeatures.md`
("Open Questions" sections) until they become a task.

---

## Language

#### Q.001 A readonly result - what may the function return? (FEATURES 50.1, D.110)
`readonly` on a result means the caller can't change what it gets. Which returns are allowed?

```fusion
class Car
    private Engine engine

    public readonly Engine function getEngine()
        return this.engine        // A: a member - the caller gets a read-only borrow (D.110) - allowed

    public readonly Engine function makeEngine()
        return Engine("V8")       // B: a new object - it moves to the caller (D.111); readonly would
                                  //    stop the caller changing its own object - allowed, or an error?

    public readonly int function power()
        return this.engine.power  // C: a number is a copy - readonly means nothing: an error
                                  //    (like `f(readonly n)` on an int, 48.3) - suggested: an error

Engine e = car.getEngine()
e.kind = "V6"                     // error: e is a read-only borrow
```

#### Q.002 `--interface` - private functions too? (FEATURES 48.4, files/Ownership.md 8)
`--interface` will show what each function does with its parameters. Public functions only, or
private ones too?

```text
> python main.py main.fusion --interface garage
module garage
  public  void   function park(Car car)          // keeps car - the call moves it
  public  Engine function engineOf(Car car)      // lends from car
  private void   function log(readonly Car car)  // A: shown too   B: hidden - public only (suggested)
```

#### Q.003 Warnings on `?.` in a comparison (files/Nullable_Values.md 5, Task 30.3)
A guarded value that is null makes every comparison false - so `!(x >= 18)` is not `x < 18`.
When should Fusion warn?

```fusion
Person x = null
if x?.getAge() >= 18 { ... }      // false
if x?.getAge() < 18 { ... }       // also false - "unknown" is neither
if !(x?.getAge() >= 18) { ... }   // true - so not the same as "< 18"

// A: warn on every `?.` value in a comparison (<, >, <=, >=)
// B: warn only on `!( ... )` around a guarded comparison - the case that surprises (suggested)
// C: no warning - the truth table in the docs is enough
// Either way: `x?.getAge() ?? 0 >= 18` makes the choice clear and gets no warning
```

#### Q.004 A method that keeps `this` (D.103, Task 48)
Today `this` is always borrowed: calling a method never moves the object, even when the method
stores `this`. Keep that, once real programs can test it?

```fusion
class Car
    void function register(Registry r)
        r.cars.add(this)          // the method keeps `this`

Car car = Car()
car.register(registry)            // A: today - car still usable, and the registry holds it too
car.paint("red")                  //    (the one place two names reach one object without byRef)
                                  // B: like a kept parameter (D.100) - the call moves car;
                                  //    car.paint(...) is then an error: "car was moved on line 5"
                                  // C: storing `this` is an error - `r.cars.add(byVal this)` stores a copy
```

#### Q.005 Form D - its syntax (FEATURES 52.1, CLS.016)
A set-up block on an abstract class or an interface gives its missing functions in place.
How is it written?

```fusion
abstract class Weapon
    string name
    abstract int function damage()

// A: the same block as form B - fields set and functions given together (suggested)
Weapon stick = Weapon() {
    name = "stick"
    int function damage() : 2
}

// B: a word saying it implements the missing parts
Weapon stick = Weapon() implements {
    int function damage() : 2
}

interface Greeter
    string function greet(string who)

Greeter hi = Greeter() {          // an interface made in place the same way
    string function greet(string who) : "Hi {who}"
}
// Also open: may its functions use the variables around it? (closures - SYN.028, not yet)
```

## Concurrency

#### Q.006 "Undone where possible" in a group service (files/Service.md group rule 7, Task 42)
An operation fails halfway: what is undone, and by whom?

```fusion
service(account, log) payment

payment.pay(100)
    account.balance -= 100        // 1. a value: can be undone (+100)
    log.write("paid 100")         // 2. has left the program: can't be undone
    bank.send(100)                // 3. fails here - BankError

// A: Fusion undoes the value changes by itself, newest first; the log line stays
// B: the developer writes how each step is undone (an `undo` block next to it)
// C: nothing automatic - the error reaches the caller; clean-up is written in `catch`
// And: should the log line wait until the whole operation has worked (written at the end)?
```

## Platforms and modules

#### Q.007 An RTOS target (FEATURES Task 41)
FreeRTOS or Zephyr have threads and timers but usually no files or console. How does Fusion
fit them?

```fusion
// fusion.toml (the setting name is a suggestion)
[target]
os = "freertos"

import File                       // A: its own small standard library for an RTOS -
                                  //    `File` doesn't exist there: "no files on this target"
                                  // B: the normal standard library; File and Console are optional
                                  //    parts a target may not have - the same error message
```

#### Q.008 Language modules - their name and how far they are trusted (FEATURES Task 49 / 39)
A language module (`Lang.Python.Fusion`) is code the compiler runs while compiling.

```fusion
import Lang.Python.Fusion         // A: its own top-level name (Task 49 today)
import fusionlib.Lang.Python      // B: under fusionlib, next to the other modules

// Trust - it runs inside the compiler:
// A: like any library - checked by its signature only (D.016)
// B: a sandbox - no files or network except the source it is given, unless fusion.toml allows more
```

## Documentation

#### Q.009 Front matter in the spec files - now or later? (FEATURES 51.5, files/DocumentationSystemProposal.md 8)
When the spec is split into `files/spec/`, does each file start with a few machine-readable lines?

```yaml
---
id: 003.002
title: Moving and borrowing
decisions: [D.014, D.100, D.101]
---
```
A: now, with the split (check.py checks them)   B: later - plain Markdown first (suggested)

#### Q.010 Two `Decisions.md` lines out of date
They say [DESIGN] for things that are built. Split them and mark the built parts?

```text
now:  CLS.013 [DESIGN] `abstract`, `sealed`, `virtual`, `override`, `protected` - reserved words, for inheritance (32.7)
A:    CLS.013 [BUILT]  `abstract`, `sealed`, `override`, `protected` (32.7)
      CLS.018 [DESIGN] `virtual` - a reserved word, not used yet

now:  SYN.024 [DESIGN] Type tests `if s is string`; `typeOf(x)` as text
A:    SYN.024 [BUILT]  Type tests `if s is string`; `typeOf(x)` as text
```

#### Q.011 The Rust rules compared with Fusion - the user's review (Notes/Rust_rules.md)
No code - the note holds the comparison table and the example line.

## Naming

#### Q.012 The language's final name (CLAUDE.md project notes)
MaiaFusion is the candidate; decided once the self-hosted compiler works fully. "Maia" is
already the name of a verification language (maia-eda.net).
