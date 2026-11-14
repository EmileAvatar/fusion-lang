[< 131 AutoDocs](131-AutoDocs.md) | [Index](index.md) | [150 Modules >](150-Modules.md) <!-- nav -->

# 140 Collections

## Collections (as built)

**Status:** [DONE 18.5] List, Map (alias Dictionary), text helpers, program arguments, console input, files, standard-library layers

**`List<T>`** (Task 18.5.1, user decisions 2026-10-11) - a growable list of any value type:
numbers, chars, bools, text, bytes, structs, and lists (`List<List<int>>`).
- **Ownership** (Task 48, `[memory] assignment = "move"` - the default since 48.9; files/Ownership.md):
  - `List<int> b = a` **moves** the list - `a` can't be used after it (a compile error:
    "'a' was moved to 'b' on line 3 - use byVal a for a copy")
  - Passing it to a function, or reading an element, **borrows** it
  - Returning it moves it to the caller
  - `byVal a` (or `byValue a`) makes a deep copy; a `byVal List<int> xs` parameter gets one
  - A struct holding a List moves with it, all of it
  - `[memory] assignment = "share"` keeps the older way: two names on one list, counted, freed
    when its last holder lets go
- It is never null - empty when declared; no setting changes that (D.138). It never holds null
  either: `add(null)`, `[a, null]`, `m[k] = null` are errors, a null that shows while running is a
  NullError (D.139, Task 52.10); `List<Car> l = [car1, car2]` adds each item
- A Map works the same way. Arrays follow once they can grow (Task 45); until then they are copied
- `xs.toList(copy = true)` (Task 32.10a.1): a List's copy, or with `false` the same list, shared; on a
  one-dimensional array, a new List with copies of its elements (sharing needs arrays on the heap -
  Task 45). Both are revisited with multi-dimensional arrays
- Built-in generic types - user-written generics come later, with classes
- In C each element type has its own small set of functions, made only when used - no boxing, no
  speed cost

```
List<int> xs = [3, 1, 2]        // a literal takes the declared type; List<int>() is empty
xs.add(10)                      // add(v), insert(i, v), removeAt(i), remove(v) -> bool, clear()
xs[0] = 7                       // reading or writing outside the list is a run-time error
int n = xs.len()                // also len(xs)
bool has = xs.contains(2)       // contains(v), indexOf(v) -> -1 when missing
xs.sort()                       // numbers, chars, bools, text; sortBy((a, b) : ...) for any type
List<int> part = xs.slice(1, 2) // start, count
List<int> big = xs.filter((int x) : x > 2)
List<string> labels = xs.map(label)          // a function (int) : string
int total = xs.reduce(0, (int sum, int x) : sum + x)
for x in xs                     // each element; a list or an array
    print("{x}")
bool same = xs == [7, 1, 2, 10] // element by element
```

* `sortBy` is stable - equal elements keep their order
* `for x in xs` gives `x` the element type; strings and other managed elements are copied
  into `x` for each pass, so the body may change the list safely. `for` loops over
  `range(...)`, a List or an array - anything else is a compile error (before Task 18.5.1
  such a loop silently ran 0..9)
* Mutating methods (`add`, `insert`, `removeAt`, `remove`, `clear`, `sort`, `sortBy`) need a
  variable (or a field / element of one) that isn't const

**`Map<K, V>`** (Task 18.5.2; also written `Dictionary<K, V>` - the same type, user decision
2026-10-11: "Map is easier to type"):
- Keys are `string`, `int` or `char`; values any value type (lists and maps too)
- A map remembers the order its keys were added - `keys()`, `values()` and `for k in m` follow it
  (as in Python and C#)
- Ownership as a List: assigning moves it, passing borrows it, `byVal` copies it; freed automatically
- In C an open-addressing hash table over the entries

```
Map<string, int> ages = Map<string, int>()   // `Map<string, int> ages` starts empty too
ages["Alice"] = 30              // adds the key, or replaces its value
int a = ages["Alice"]           // reading a missing key is a run-time error naming the key
bool known = ages.has("Bob")
int b = ages.get("Bob", 0)      // the value, or the default when the key is missing
bool gone = ages.remove("Bob")  // false when it wasn't there
List<string> names = ages.keys()        // also values(), len(), clear()
for name in ages                // the keys
    print(name)
bool same = ages == other       // the same keys with equal values, in any order
```

* `m["a"][0] = 5` needs `"a"` to be there already; only the final `m[k] = v` adds a key
* A name after `.` may be a word Fusion reserves for later (`m.get`, `x.set`) - after a dot
  it can only be a field or method name

**Text and lists** (Task 18.5.3) - each also a method (`s.split(",")`, `parts.join(", ")`):
* `split(s, sep)` - every piece between separators, empty ones too (`"a,,b"` -> `a`, `""`,
  `b`; `""` -> one empty piece, as Python); an empty separator splits into characters
* `join(parts, sep)` - a `List<string>` into one string
* `lines(s)` - the lines without their `\n` (a `\r` before it is dropped too); a final
  newline doesn't make an empty last line
* `words(s)` - the pieces between runs of spaces, tabs and newlines; never an empty word

**Program arguments, console input, exit** (Task 18.5.4):
* `void function main(string... args)` (user decision 2026-10-11 - "List<string> args seems a
  bit too wordy"):
  - `args` is a `string[]` of any length (`len(args)`, `args[0]`, `for a in args`); main may also take nothing
  - The program's name and `--headless` are not in it
  - On Windows the arguments are read as UTF-16 and turned into UTF-8, so accented ones arrive intact
  - `...` is only for main for now - functions taking any number of values come later
  - Other main parameters are an error (before Task 18.5.4 they were accepted with a warning and ignored)
* `readLine()` - the next line of input without `\n` / `\r\n`, of any length; `""` at the
  end of input. `isEndOfInput()` - true when nothing is left to read. On Windows the console
  reads UTF-8
* `exit(code)` - ends the program at once with that exit code (the "Press any key" wait
  still happens when someone is at the console)
* `run(command)` (Task 28.1.1) - runs another program through the system shell (`cmd /c` on
  Windows, `/bin/sh -c` elsewhere):
  - It **waits** until the program ends and returns its exit code
  - A program that runs and fails is not an error - its code comes back (a command that doesn't
    exist gives the shell's own non-zero code)
  - Only a shell that can't be started is a `ProcessError`
  - Output printed before the call is flushed first, so lines stay in order
  - On Windows the command is passed to `cmd` exactly as written, quotes included
    (`run("\"C:/My Apps/x.exe\" \"a b\"")`)
  - Not waiting: `run("start notepad")` on Windows
  - Running programs will be a declared capability (Task 39)
  - Later: capturing a program's output, and a separate `start`

**Files** (Task 18.5.5):
* `readText(path)` (the whole file - it must be valid UTF-8 text; a UTF-8 byte-order mark at
  the start is dropped, as C# does), `readLines(path)` -> `List<string>` (as `lines`),
  `writeText(path, s)` (creates or replaces), `appendText(path, s)`, `readBytes(path)` ->
  `bytes` and `writeBytes(path, b)` for binary files, `fileExists(path)` (a file, not a
  folder), `deleteFile(path)`
* Files are read and written byte for byte - no newline translation
* Paths are relative to the folder the program runs in, `/` or `\\` between folders; names
  with accents work on Windows (the wide-character file functions)
* A failure - a missing file, no permission, a missing folder - is a `FileError` naming the file
  and the reason (`FileNotFoundError`, `PermissionError`, `FileReadError`, `FileWriteError`):
  caught with `catch FileError e` or captured (`string s, Error err = readText(path)`), else it
  stops the program ([120 Errors](120-Errors.md), Task 26); `fileExists` checks first
* File access will be a declared capability (Task 39)

**Standard-library layers** (Task 18.5.6 - "layer the stdlib from day one"):
- The lesson from D, whose library assumed a garbage collector and split the ecosystem when GC
  became optional
- `fusion.toml` `[stdlib] layer` says how much a project may use; each layer adds to the one before it:
* **core** - no heap: numbers, chars, bools, fixed arrays, structs of those, `range`, `len`
  of an array, `toByte`, `charCode` / `fromCharCode`. For the smallest embedded devices
* **alloc** - adds memory: text, `bytes`, `List`, `Map` and every function on them
* **std** (the default) - adds the operating system: `print`, `readLine` / `isEndOfInput`,
  files, `exit`, `run`, and main's arguments (`string... args`)
* Using something above the project's layer is a compile error, once per place:
  "'print' needs the std layer, but this project uses alloc ([stdlib] layer in fusion.toml)";
  in a core project any text, bytes, List or Map - a value or a declared type - is refused
* `print` is std, as console output is an operating-system service (Rust's `core` / `alloc`
  can't print either); an embedded program reports through its own device
* Every built-in is tagged with its layer (src/semantic/name_resolver.py) - the groundwork
  for capability checks (Task 39): a library will declare the layer it needs

Example program using all of it: `examples/wordcount/` - modules, a file, `List`, `Map`,
`sortBy` and the text helpers (Task 18.5.7).

[< 131 AutoDocs](131-AutoDocs.md) | [Index](index.md) | [150 Modules >](150-Modules.md) <!-- nav -->
