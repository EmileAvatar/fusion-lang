[< 140 Collections](140-Collections.md) | [Index](index.md) | [160 GameExample >](160-GameExample.md) <!-- nav -->

# 150 Modules

Contents: [File Organization](#file-organization) | [Module Definition](#module-definition) | [Class Files](#class-files) | [Import Syntax](#import-syntax) | [Visibility Control](#visibility-control)

## Module System

**Status:** [DONE 18.4, 32.2] module folders, `import`, aliases, `public` / `internal` / `private`, `namespace`,
`--interface` (MOD.001, MOD.002); importing only some names [DESIGN] (MOD.005). The sections after
"As built" are the **earlier design** - see the note there

Description: Organized code structure with clear dependencies.

**As built (Task 18.4.2, user decisions 2026-10-10; classes since Task 32)** - a module holds structs,
classes, interfaces, enums, error types, functions and module variables:

* **A module is a folder** next to the program's main file:
  - Every `.fusion` file in `money/` belongs to module `money`; they share each other's names freely
  - `geometry/shapes/` is module `geometry.shapes` (folders nest; modules don't contain each other)
  - The program itself is just its main file, so a folder of separate programs (like `examples/`) still works
* **Imports come first in a file, and each file imports what it uses** (as in Go, Java and
  Python):
  ```
  import money                    // money.round(x), money.Price, money.make(5)
  import money.Price              // Price - one name, no prefix
  import money.*                  // every name, no prefix
  import geometry.shapes          // used by the last part of its path: shapes.area(2)
  import lib.utils as libutils    // an alias: libutils.trim(s)
  money.Price p = money.make(100) // a struct from another module in a type
  ```
* **Each module is loaded once**, from one list of loaded modules: imports may criss-cross
  (`money` imports `tax`, `tax` imports `money`) without looping
* **Name rules:**
  - A file's own names win over a `.*` import
  - The same name from two `.*` imports is an error where it's used ("'f' is ambiguous: a.f or b.f -
    use the module prefix")
  - `import money.Price` next to a declared `Price` is an error
  - **Two different modules with the same name** in one file (`shop/utils`, `lib/utils`) are an error -
    give one an alias with `as`
  - A local variable may share a name with an imported one; inside its block the variable wins
* Only the main file may have `main`. A module can't be named after a built-in type class
  (`String`, `Int`, ...) or contain `__`
* All modules compile into one C file; `money.round` is `fu_money__round` there, and two
  Fusion names that would share a C name are reported
* **Module interfaces** (Task 18.4.4): `python main.py main.fusion --interface [module]`:
  - Prints the public structs, enums, error types, module variables and functions of the modules a
    program imports, with their types and defaults: what other modules may rely on
  - Internal names too, never private ones: decided (D.115), not built yet
  - The groundwork for library signatures and capability checks (Task 39)
  ```
  module money
      public struct Price
          int cents
      public Price function make(int cents)
      public string function show(Price p)
  ```
* Example: `examples/shop/` - a program of three files in two modules
* **`public` / `internal` / `private`** (Task 18.4.3; 32.2a; 32.2h, user decisions 2026-10-30):
  - Structs, classes, enums, error types and functions are public unless written `internal`
  - Module variables are private to their module unless written `public` / `internal`
  - `internal` means the namespace - a file without one: its module
  - Other modules use public names through `money.round`, `import money.round` or `import money.*`
    (public names only); a module's own files see all of each other's names
  - `private` on a top-level struct, class, enum, error type or function is an error ("write 'internal'")
  - A public function or struct can't use an internal struct of its module in its parameters, result
    or fields ("make 'Secret' public too") - other modules would get values of a type they can't name
  ```
  public struct Price          // other modules may use it
      int cents
  public Price function make(int cents) : Price(cents + fee())
  internal int function fee() : 50   // only module money (or its namespace) sees it
  ```
* **`namespace Shop.Tools`** (Task 32.2h): the file's first line, before the imports - a line, not a folder
  - Modules whose files share a namespace see each other's internal names and class members
  - Fusion's own libraries use `namespace Core`

**The earlier design** (the sections below, before Task 18.4) - not built, kept for review:

| Earlier design | Today |
|---|---|
| A `module.fusion` file with `module X` and `export` lines | **No** (user, 2026-11-12; D.135): a module is not a separate file - a line at the top of a file says which namespace / module it belongs to (built: `namespace`); its variables, interfaces, structs and classes belong to that module. Folder or line: [Q.013](../../OpenQuestions.md) |
| `export` / not exported | Replaced by `public` / `internal` / `private` (built) |
| One class per file, the file named after the class | **No** (user, 2026-11-12; D.135): a file may hold many classes - not a strict requirement |
| A class nested inside a class | Not decided |
| `import X`, `import X.Name`, `import X.*` | Built as shown above |
| A module compiled to a DLL | Later (user, 2026-11-12): the folders and files of one module compile into one library (`.dll` / `.so`), ready for a larger application - postponed, needs `extern` (MOD.003) |

---

### File Organization

Description: Clear structure for maintainability.

* **Rules**
     * One class per file (class name matches filename)
     * Module groups related files in directory
     * Special module.fusion file defines module
     * Subclasses can be nested within class file
     * Modules cannot be nested in other modules

* **Directory Structure**

```
project/
├── Spaceships/
│   ├── module.fusion          // Module definition
│   ├── Spaceship.fusion        // One class
│   ├── Warship.fusion          // One class
│   └── CargoShip.fusion        // One class
├── Weapons/
│   ├── module.fusion
│   ├── Laser.fusion
│   └── Missile.fusion
└── main.fusion
```

---

### Module Definition

Description: Define module in module.fusion file.

```
// Spaceships/module.fusion
module Spaceships

export Spaceship
export Warship
export CargoShip

// Private helper (not exported)
void function validateShipName(string name)
    return name.length > 0
```

---

### Class Files

Description: One class per file with optional nested subclasses.

```
// Spaceships/Spaceship.fusion
class Spaceship
    string name
    float speed
    
    constructor(string name, float speed)
        this.name = name
        this.speed = speed
    
    void function start()
        print("{name} started")
    
    // Nested subclass allowed
    class Engine
        float power
        
        constructor(float power)
            this.power = power
```

---

### Import Syntax

Description: Multiple ways to import modules and classes.

```
// Import entire module
import Spaceships

// Use with module prefix
Spaceship ship = Spaceships.Spaceship("Enterprise", 100.0)

// Import specific class
import Spaceships.Spaceship

// Use without prefix
Spaceship ship = Spaceship("Enterprise", 100.0)

// Import all from module
import Spaceships.*

// Use all exported classes
Spaceship ship = Spaceship("Enterprise", 100.0)
Warship warship = Warship("Destroyer", 150.0, 50)
```

---

### Visibility Control

Description: Control what is accessible from outside module.

```
// module.fusion
module Spaceships

export Spaceship        // Public: can be imported
export Warship          // Public: can be imported

// CargoShip not exported - internal to module only

void function internalHelper()  // Not exported - module-private
    // ...
```

[< 140 Collections](140-Collections.md) | [Index](index.md) | [160 GameExample >](160-GameExample.md) <!-- nav -->
