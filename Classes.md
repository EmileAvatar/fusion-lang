# Classes: visibility, constructors, static set-up, Default

A design document for Task 32.2 and 32.5 (user decisions 2026-10-30). Status: built -
visibility (32.2a), constructors (32.2b), statics (32.2c: tests/test_statics.py), form B on
any variable (32.2d: tests/test_setup_blocks.py); the rest designed. Every permutation is in a truth table,
so each rule can be checked at a glance and turned into a test.

---

## 1. Visibility - what is public when nothing is written

| Where | Thing | Default | Written out | Notes |
|---|---|---|---|---|
| Inside a class | field | **private** | `public string name` | the class's own code only |
| Inside a class | function (method) | **public** | `private void function helper()` | |
| Inside a class | constructor | **public** | `private constructor()` | a class with none still gets the default `Car()` |
| Inside a class | static field / method | as a field / function | | private static fields, public static methods |
| Module level | struct | **public** | `private struct Helper` | private: only inside its module |
| Module level | class | **public** | `private class Helper` | a helper class strictly for the module |
| Module level | enum | **public** | `private enum Mode` | |
| Module level | function | **private** - becomes **public** with 32.2h | `public void function run()` | today's rule (Task 18.4.3, 2026-10-10) |
| Module level | module variable / constant | **private** - its module | `public int rate = 5` | today's rule (Task 44.1) |

**Planned (32.2h - files/FusionTemplate.md section 4):** three levels - `private` (the class;
on a top-level item an error, write `internal`), `internal` (the namespace; without one, the
module), `public`. `[visibility] required = true` makes writing the level mandatory.

**Rule of thumb:** types are public, helpers are private. A thing is made private when it is
internal to the module and not useful outside it.

---

## 2. Constructors - who may call them

| Constructor | Form A (`= new Car()`) in its class | Form B (`= new Car() { }`) in its class | Form C (`static { }`) in its class | A method of the class | Another class / module |
|---|---|---|---|---|---|
| public (the default) | yes | yes | yes | yes | yes |
| private | **yes** | **yes** | yes | yes | **no - a compile error** |

- A private constructor is how a class makes a fixed set of objects or acts as a factory:
  `public const static Car HONDA = new Car("Honda")` (form A) works, `new Car("x")` in
  another class doesn't
- **Several constructors:** chosen by the number and types of the arguments; two that can't be
  told apart are a compile error. `this(...)` on a constructor's first line calls another;
  constructors calling each other in a circle are a compile error

---

## 3. Static set-up - three forms

```fusion
class Garage
    // Form A - direct
    public const static Car CAR = new Car()

    // Form B - self set-up: the block works on CAR3
    public const static Car CAR3 = new Car() {
        CAR3.setEngine("V6")
        CAR3.speed = 4
    }

    // Form C - the static block: any static of the class
    public const static Car CAR2
    static {
        CAR2 = new Car()
        CAR2.setEngine("V8")
        CAR3.setMake("Honda")
    }
```

| Form | Runs | May read | May change | Notes |
|---|---|---|---|---|
| A - direct | 1st, top to bottom | statics already set up | its own field (the value) | |
| B - self set-up | 2nd, top to bottom | statics already set up (form A, B above it) | **its own field only** | |
| C - `static { }` | 3rd, top to bottom | any static of the class | **any static of the class** | gives a `const static` declared without a value its one value |

| Question | Answer |
|---|---|
| Does public / private / const change the order? | No - A, then B, then C, whatever they are |
| When can another class use the statics? | Only once form C has finished |
| In which order are classes set up? | By dependency - Engine before Car when Car's set-up uses Engine |
| How does the compiler find a dependency? | What forms A, B and C name - classes, statics, constructors, methods - then what those constructors and methods name, until nothing new is found |
| Two classes whose set-up uses each other? | A compile error that shows the whole circle, e.g. `Car -> Engine -> Parts -> Factory -> Car`: "Factory can't use Car - Car is still being set up (Car -> Engine -> Parts -> Factory -> Car)" |
| Something the compiler can't see in advance (a call through a function value)? | A clear run-time error: "Car's statics aren't set up yet" |
| When does it all run? | Before `main` |
| When are statics freed? | Last, when the program ends (Object_Lifetime.md U10) - after module variables |
| Static methods | No `this`: `Car.make("x")` |
| Plain statics | `static int count` - set up like form A (0 when no value is given) |

---

## 4. Form B for any variable - not only statics

Form B (a block right after the value) works on any variable, field or static:

```fusion
Car mine = new Car() {
    mine.setEngine("V6")
}
List<string> names = List<string>() {
    names.noDuplicates()          // planned list options (Task 32.14)
    names.readOnlyAfterSetup()
}
```

| Where | Form B allowed | The block may change |
|---|---|---|
| A static field | yes | that field only |
| A local variable | yes | that variable only |
| A field of a class (its default) | yes | that field only |
| An array / List / Map | yes | that collection only - e.g. no duplicates, no null, read only (planned options) |

A set-up block may change the variable it sets up even when it is `const` or `let` - the
object is still being set up (user, 2026-10-30; built with 32.2e).

Built (32.2d): a class field's value may be any expression - each constructor sets the field
and runs its block first, in field order, before its own body (once, also when it hands over
with `this(...)`). Changing another variable in the block is a compile error.

**Not the builder pattern:** form B sets up one variable right where it is made. A builder (a
separate object that collects settings, then `build()` makes the result) is a different idea,
noted for later (FEATURES.md Later).

---

## 5. `Default` - an object that is never null

```fusion
interface Default
    constructor()                 // a constructor with no arguments

class Settings implements Default
    private constructor()         // may be private - the compiler calls it
        ...
```

| Class implements `Default`? | `Settings s` (no value) | `Settings s = null` | Form B on it |
|---|---|---|---|
| no | **null** | allowed | yes, when a value is given |
| yes | **an object is made** - the compiler calls `Settings()` | **never null:** the old object is let go (freed if nothing else holds it) and a new default object made in its place | yes - sets it up further |

- The same idea as an array, List or Map: never null, empty when declared - they implement
  `Default` themselves
- Elsewhere this is called a non-nullable reference type (C#, Kotlin); Rust names the "has a
  ready value" part the `Default` trait
- Needs interfaces (Task 32.5)

---

## 6. Printing an object - `ToString`

| The class implements `ToString { string toString() }`? | `print("{car}")`, a struct's field, a collection's element, `toCSV` |
|---|---|
| yes | its `toString()` |
| no | the class name only (`Car`) - and a **warning**: it doesn't implement ToString |

A struct keeps its built-in text (`name : value,...`). ToString needs interfaces (Task 32.5);
until then every object prints its class name, with the warning. Built (32.2f,
tests/test_object_text.py): `print`, `format`, `"{car}"`, `toString(car)`; one warning per
class; a null object prints `null` (as in most languages - no NullError). Lists of objects
and `toCSV` of objects can't be printed whole yet (no List prints whole today).

---

## 7. Decisions log

| Date | Decision |
|---|---|
| 2026-10-30 | Class fields private, functions public, constructors public by default; a class always has a default constructor |
| 2026-10-30 | Module level: structs, classes, enums public by default; functions and module variables private (unchanged) |
| 2026-10-30 | A private constructor may be used by forms A and B (and C, and the class's methods) - never from outside |
| 2026-10-30 | Static set-up forms A, B, C - in that order; B changes only its own field and reads statics already set up; C changes any static; classes set up by dependency; a circle is a compile error that shows the whole chain |
| 2026-10-30 | Form B works on any variable, field or static - including arrays / Lists / Maps (options like no duplicates, read only) |
| 2026-10-30 | `Default` interface - a constructor with no arguments (may be private); a variable of the type is never null, the object made automatically |
| 2026-10-30 | `Default` and null: `s = null` on a Default type lets the old object go and makes a new default one - the variable is never null, even right after `= null` |
| 2026-10-30 | Printing an object: `ToString` interface; without it the class name only, with a warning |
| 2026-10-30 | The builder pattern - noted for later, a different idea from form B |
