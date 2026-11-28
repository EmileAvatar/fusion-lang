# How a Fusion file is laid out

The layout of a `.fusion` file (user decisions 2026-10-30). Two things are **enforced** by the
compiler; the rest is the **preferred layout** - Fusion's own libraries follow it, and other
code is free to order things as it needs. Every construct with its modifiers (`public`,
`internal`, `private`, `static`, `const`, `readonly`, `byVal`, ...) and what leaving one out
means: `files/showcase/Fusion_template.fusion`.

---

## 1. Enforced

| Rule | Notes |
|---|---|
| `namespace` comes first, if the file has one; `module` next | Optional - the folder gives both, and a line written must match it (D.204) |
| `import` lines come next, before anything else | Optional |
| `Fusion.Core` is always imported | Never written - the core of the language (print, write ...) is there in every file; `Fusion.Core.print(...)` its full name (D.208) |

A namespace is a **folder** of modules, and a module a folder of files (Task 57.1, D.204): `SQL/Database/` is
namespace SQL, module Database - a name in full is `Namespace.Module.Name`. The `namespace` and `module` lines are
optional; when written they must match the folder (an error otherwise). The main file is the program - in no
namespace or module.

---

## 2. The preferred layout

```text
<FileName>.fusion

namespace <Name>.<SubName>          // optional - enforced first when present
import <module>                     // optional - enforced before everything below

<interfaces>
<structs>
<static variables>
<static initialiser>

<class>
    <static variables>
    <static initialiser>
    <structs>
    <internal / private classes>
    <constructors>
    <properties>                    // properties and functions in any order -
    <functions>                     // as long as they come after the constructors
</class>

<class>                             // a file may hold several classes - e.g. one used above
    ...
</class>
```

---

## 3. An example

```fusion
// Fusion/Collections/RingBuffer.fusion
namespace Fusion
module Collections

import IO

interface Sized
    int function size()

struct Slot
    int index
    string value

class RingBuffer implements Sized
    static int made                         // static variables
    static {                                // static initialiser
        made = 0
    }

    private List<Slot> slots                // fields
    private int next

    constructor(int capacity)               // constructors
        ...

    int function size() : slots.len()       // functions
    void function add(string value)
        ...
```

`implements`, interfaces, `static` and `namespace` are designed - see `files/Classes.md` and
`files/FEATURES.md` Task 32 for what is built.

---

## 4. Visibility - what applies when nothing is written

A module inside a namespace (`Shop/Pricing/`) is **structured** (D.211, D.205): it holds classes, interfaces, structs,
enums, error types, constants, and static variables and functions - normal functions belong in a class; a static
function is used sparingly (a factory, or work that fits no class - as print and write). A module folder without a
namespace (`money/`) and the main file are free.

| Item | Nothing written means | Notes |
|---|---|---|
| field of a class or struct | `private` | |
| module variable | `private` - its module | in a module inside a namespace: `static`, written out (D.212) |
| function, constructor | `public` | at the top of a module inside a namespace: `public static` - the compiler adds `static` with a warning asking for it to be written (D.212) |
| class, interface, enum, struct | `public` | an interface or enum is static already |
| `internal` | the namespace | in a file without a namespace: its module, like private |
| `private` on a top-level class, struct, enum or interface | its module only (D.212) | `internal` shares it with the whole namespace |
| `private` on a top-level function | an error | write `internal` (its namespace), or put it in a class |
| `private` inside an interface | an error | |

`[visibility] required = true` (built, Task 32.2h) makes writing the level mandatory - a
missing one is an error. `namespace` and `internal` are built too. Details: `files/Classes.md`
section 1.
