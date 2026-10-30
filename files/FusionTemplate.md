# How a Fusion file is laid out

The layout of a `.fusion` file (user decisions 2026-10-30). Two things are **enforced** by the
compiler; the rest is the **preferred layout** - Fusion's own libraries follow it, and other
code is free to order things as it needs. Modifiers (`public`, `internal`, `private`,
`static`, `const`, ...) will be added to this template later.

---

## 1. Enforced

| Rule | Notes |
|---|---|
| `namespace` comes first, if the file has one | Optional - Fusion's own libraries use it (`namespace Core`); an app only to split a large program into logical parts |
| `import` lines come next, before anything else | Optional |
| `Core` is always imported | Never written - the core foundation of the language is there in every file |

A namespace is a **line, not a folder**: it says where the file's contents belong
(`Namespace.Module.Class.Function` - later used to map what belongs where). Files stay where
they are; the core modules (IO, Graphics, ...) sit side by side.

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
// RingBuffer.fusion
namespace Core.Collections

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

`implements`, interfaces, `static` and `namespace` are designed - see `Classes.md` and
`FEATURES.md` Task 32 for what is built.

---

## 4. Visibility - what applies when nothing is written

| Item | Nothing written means | Notes |
|---|---|---|
| field of a class or struct | `private` | |
| module variable | `private` - its module | |
| function, constructor | `public` | |
| class, interface, enum, struct | `public` | |
| `internal` | the namespace | in a file without a namespace: its module, like private |
| `private` on a top-level class, struct, enum, interface or function | an error | nothing could use it - write `internal` |
| `private` inside an interface | an error | |

`[visibility] required = true` (planned) makes writing the level mandatory - a missing one is
an error. Details: `Classes.md` section 1.
