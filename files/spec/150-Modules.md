[< 140 Collections](140-Collections.md) | [Index](index.md) | [160 GameExample >](160-GameExample.md) <!-- nav -->

# 150 Modules

**Contents**

- [Module System](#module-system)

## Module System

**Status:** [DONE 18.4, 32.2, 57] module folders, `import`, aliases, `public` / `internal` / `private`, namespaces
as folders, `[libraries]`, full names, Fusion's own modules, `--interface` (MOD.001, MOD.002, MOD.012); importing only
some names [DESIGN] (MOD.005)

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
  - Internal names too, never private ones (D.115)
  - A module inside a namespace shows `namespace SQL` and `module Database`, its functions and variables
    `static` (Task 57.6); `--interface SQL` shows every imported module of the namespace
  - The groundwork for library signatures and capability checks (Task 39)
  ```
  module money
      public struct Price
          int cents
      public Price function make(int cents)
      public string function show(Price p)
  ```
* Example: `examples/13_projects/shop/` - a program of three files in two modules
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
* **The folder gives the namespace and module** (Task 57.1, D.204): `Shop/stock/` is namespace Shop, module stock;
  `money/` is module money, without a namespace
  - `namespace Shop` and `module stock` - optional lines, first in the file, before the imports; one that doesn't
    match the folder is an error naming both ("write 'namespace Shop', or move the file")
  - Modules of one namespace see each other's internal names and class members (D.207)
  - The main file is the program - a `namespace` or `module` line in it is an error
* **A structured module** (Task 57.2, D.211, D.212) - a module inside a namespace:
  - Holds classes, interfaces, structs, enums, error types, constants, and static variables and functions -
    normal functions belong in a class; a static function is used sparingly
  - A function or variable at the top without `static` is static all the same - the compiler adds it, with a
    warning: "write 'public static' before it, or put it in a class"
  - A function is public or internal; a variable private by default (`static int made`); a class, struct, enum or
    interface may be `private` - its module only (`internal` - the namespace)
  - A module folder without a namespace (`money/`) and the main file are free, as before
* **External libraries** (Task 57.3, D.206, D.213):
  - fusion.toml lists each library the project imports - its namespace and its folder, relative to the settings
    file (as a VB.NET project reference):
    ```toml
    [libraries]
    SQL = "C:/vendor/SQL"
    "com.example.SQL" = "../libs/com/example/SQL"
    ```
    then `import SQL.Database` finds `C:/vendor/SQL/Database/`
  - Not listed: `import "C:/vendor".SQL.Database` - the folder holding the namespace, then the names
  - Searched in order: the program's folder, then `[libraries]`; a module in two places is an error naming both
* **Importing a namespace, full names** (Task 57.4, D.208, D.209):
  ```fusion
  import SQL as Q                  // a namespace: Q.Database.name(), Q.Pool.size(), Q.Database.Conn c
  import SQL                       // SQL.Database.name()
  import SQL.Database              // Database.name(), and the full name SQL.Database.name()
  import B.Database as BD          // a second Database - an alias needed (BD.name(), B.Database.name())
  ```
  - A namespace import loads only the modules the file uses; `Q.Nope.x` is an error ("Namespace SQL has no module
    'Nope'")
  - Two imported modules with the same name are an error until one (or both) gets an alias
* **Fusion's own modules** (Task 57.5, D.208, D.210): the namespace `Fusion` is reserved for them - a folder or a
  `[libraries]` name Fusion is an error
  - `Fusion.Core` - the built-ins (print, write ...) - is always there; `import Fusion.Core` changes nothing, and
    `Fusion.Core.print("x")` is print's full name
  - `Fusion.Currency` (src/stdlib/Fusion/Currency/) is added when a program uses money, or with `import
    Fusion.Currency`; `Fusion.Currency.Currency.places("JPY")` its full name

**Words (D.136, D.204, D.205):**

| Word | What it is | Example |
|---|---|---|
| Namespace | A supplier's group of modules - a folder holding them | `Fusion` (Fusion's own), `SQL`, `com.example.SQL` |
| Module | A folder of one or more files: classes, interfaces, structs, enums, static variables and functions | `SQL/Database/` |
| A full name | `Namespace.Module.Name` | `SQL.Database.createConnection(...)` |
| A library | One module compiled to one library - later, needs `extern` (MOD.003, FEATURES 57.8) | `Fusion.IO.dll` |

**The truth table (Task 57, Rule 4c)** - each row a test in tests/test_namespaces.py:

| Case | Result |
|---|---|
| A file in `SQL/Database/`, no lines | namespace SQL, module Database |
| ... with `namespace SQL` / `module Database` / both | the same |
| ... with `namespace Shop` or `module Data` | an error naming the line and the folder |
| A file in `money/` with `namespace SQL` | an error: a module without a namespace |
| The main file with `namespace` or `module` | an error: the main file is the program |
| `internal` in `Shop/stock`, used from `Shop/till` | allowed - one namespace |
| `internal` in `Shop/stock`, used from `Office/desk` or the main file | an error |
| In a namespace: a function or variable with `static` | as written |
| In a namespace: a function or variable without `static` | static, with a warning |
| In a namespace: a constant, enum, interface, error type, class, struct | allowed as written |
| In `money/` (no namespace): a function without `static` | free - no warning |
| `private` on a top-level class, struct, enum, interface | its module only |
| `private` on a top-level function | an error |
| `import SQL.Database` - next to the main file / in `[libraries]` / with its path | found |
| ... in two places | an error naming both |
| ... nowhere | an error |
| `import SQL as Q` / `import SQL` | `Q.Database.x` / `SQL.Database.x`; only the modules used loaded |
| `Q.Nope.x` | an error: the namespace has no module Nope |
| `SQL.Database.x` after `import SQL.Database` (or `as D`) | the full name works |
| `import A.Database` and `import B.Database` | an error until one has an alias |
| `import Fusion.Core` / `import Fusion.Currency` | accepted; Fusion.Core is always there |
| `import Fusion.IO`, a folder or `[libraries]` name Fusion | an error - Fusion is reserved |

The earlier design - a `module.fusion` file with `export` lines, one class per file - was never built and is
replaced by the folders above (D.135, D.204).

[< 140 Collections](140-Collections.md) | [Index](index.md) | [160 GameExample >](160-GameExample.md) <!-- nav -->
