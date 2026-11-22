# Single values, arrays, lists and maps

The four ways Fusion holds data: what each can do, when to use it, and when not to.
Decisions by the user, 2026-10-27. Status marks: **built** (works today) and **planned**
(designed, scheduled in `files/FEATURES.md`). Every built-in method is listed in
`files/Builtins.md`. Null rules: `files/Nullable_Values.md`.

---

## 1. Overview

| | Single value | Array `T[]` | List `List<T>` | Map `Map<K, V>` |
|---|---|---|---|---|
| Holds | one value | many values of one type, in order | many values of one type, in order | values found by a key |
| Example | `int age = 36` | `int[] scores = [90, 75]` | `List<string> names = ["Ada"]` | `Map<string, int> ages` |
| Empty when declared | 0, `""`, false, ... | `[]` (planned) | empty | empty |
| Can be null | no | no (a setting may allow it) | no (a setting may allow it) | no (a setting may allow it) |
| Size | - | grows and shrinks **at the end only** (planned; fixed today) | grows and shrinks anywhere | grows and shrinks |
| Read by | its name | position `a[i]`, checked | position `xs[i]`, checked | key `m["Ann"]` (KeyError if missing) or `m.get(k, default)` |
| Add | - | at the end: `a.add(4)` (planned) | anywhere: `add`, `insert` | `m[key] = value` |
| Remove | - | from the end (planned) | anywhere: `removeAt`, `remove` | `m.remove(key)` |
| Reorder / sort | - | no | `sort`, `sortBy` (a kept sort order planned) | keeps the order keys were added |
| Duplicates | - | allowed | allowed | **no**: each key once (adding it again replaces the value, by default) |
| `b = a` (normal code) | a copy | an independent copy (shared with Task 45) | **shared** (`byVal a` copies) | **shared** (`byVal a` copies) |
| Cost of adding | - | cheap at the end | cheap at the end, slower in the middle (later items move up) | cheap |
| Status | built | built (fixed size); growing planned | built | built |

#### Shared or copied - the rule of thumb (user, 2026-10-29)

Arrays, Lists and Maps are treated like values in one way - **never null, just empty** - but
are **references** (shared) everywhere except **inside a struct**, where they are copied with it.

| Where | `b = a`, passing to a function, returning | Written with `byVal` | Written with `byRef` |
|---|---|---|---|
| Normal code - a variable, a parameter, a class field, an element of a List / Map | **shared** - a change through `b` shows in `a` | a copy (deep) | shared (the default, written out) |
| A field of a struct | **copied** with the struct (`byVal`) | copied (the default, written out) | shared - `byRef List<int> items` |

```fusion
List<int> a = [1]
List<int> b = a              // the same list
b.add(2)                     // a has 2 items too
List<int> c = byVal a        // a copy - c.add(3) leaves a alone
void function grow(List<int> xs)            // shared - xs.add(9) changes the caller's list
void function look(byVal List<int> xs)      // a copy

struct Order
    List<string> items       // copied when the Order is copied
    byRef List<string> log   // shared by the copies
```

The counting (files/Object_Lifetime.md section 5) frees a List or Map when its last holder lets go.
**Arrays** follow the same rule once they live on the heap and know their own length (Task
45); until then an array keeps today's behaviour (fixed size, copied).

**Planned - moving by default (Task 48, user 2026-10-31 - files/Ownership.md):** the table above
is today's rule. With Task 48 `List<int> b = a` **moves** (a is no longer usable), `byVal`
copies, and code that reads an element or passes a List borrows it. A collection inside a
struct only lends itself - `List<string> xs = order.items` is a borrow, never a move
(files/Ownership.md truth tables 1, 2). Arrays follow the same rule once on the heap (45.10). A
struct's fields are only ever borrowed; the whole struct moves (Decisions.md D.025, D.026).
`[memory] assignment = "share"` keeps today's sharing.

**Planned - `fixed(n)` (Task 47.5, user 2026-10-31 - Decisions.md D.064):** `fixed` limits only
the **size** - at most n characters or slots; the values may still change. `const` is
different: nothing changes, neither the length nor the values. The compiler guarantees a
fixed string or collection never exceeds its total - for limited memory and hot paths.
Lower is fine, more is an error (never cut). It starts empty and grows up to its maximum;
its memory is reserved once.
```fusion
fixed(10) string name                        // at most 10 characters
fixed(10) int numbers[]                      // at most 10 elements
fixed int numbers[10]                        // the same - the size written in the array
fixed(14) List<Person> people                // at most 14 people
fixed(10) Map<int, fixed(15) string> codes   // at most 10 keys, each value at most 15 characters
```

**In one line each:**
- **Single value**: one thing - an age, a name, a flag
- **Array**: a sequence you build up at the end and read by position - simple and fast
- **List**: a sequence you change anywhere - insert, remove, reorder, sort
- **Map**: values you look up by a key - a name, an id, a code

---

## 2. Single values

```fusion
int age = 36
string name = "Ada"          // "" when not set - never null
bool ready                   // false
char grade = 'A'
byte flags                   // 0x00
```

- **Use for:** one fact about something
- **Don't use for:** a numbered series (`score1`, `score2`, `score3` ...) - that is an array
  or a list
- A struct groups several single values that belong together (`Person` with name and age)

---

## 3. Arrays

#### Today (built)

```fusion
int[] scores = [90, 75, 60]      // size from the values
float[3] buffer                  // three zeros
scores[0] = 95                   // every index is checked: outside is an IndexError
print("{@1}", len(scores))       // 3
```

A plain array keeps its size until it is replaced as a whole. `int[] numbers` with no size or values is an
empty array, size 0 (Task 45.2, D.141); a struct field written without a size lives on the heap (45.10).
Every array acts as an object of the built-in `Array` class: `Array.length(a)` is `a.length` (45.1, D.142).
The full design - plain, `fixed`, growable `int:[]`, 2 and 3 dimensions, storage: Decisions.md D.141-D.154,
D.163, D.164; every form and what it can do: section 8c.

#### Arrays that grow at the end (user, 2026-10-27 - built: Task 45.3, `int:[]` / `int[[]]`; `+` and `slice` planned)

An array grows and shrinks **only at its end**. Nothing is inserted in the middle, so no item
ever moves to another position.

```fusion
int:[] numbers             // [] - empty, can grow (also int[[]] numbers, int numbers[[]])
numbers.add(4)             // [4]     - index 0, length 1
numbers.add(6)             // [4, 6]
int last = numbers.removeLast()   // 6, [4] left - the item given back (pop() the same - quick typing)
int[] more = numbers + [7, 8]        // a + b: b's items after a's -> [4, 7, 8]
int[] all = a + b + c + d            // any number at once - all of the same type (built: Task 45.4)
int[] part = more.slice(1, 2)        // [7, 8] - a copy; more is unchanged
```

Like JavaScript's `slice`, taking a part never changes the original:

```javascript
const fruits = ['apple', 'banana', 'mango', 'grape'];
const result = fruits.slice(1, 3);   // ['banana', 'mango']
console.log(fruits);                 // unchanged
```

(JavaScript's `slice(1, 3)` means "from 1 up to 3"; Fusion's `slice(start, count)` means
"count items from start", and `sliceAt(start, end)` means "from start to end" - see section 7.)

**Looping:** the collection being looped over can't be changed inside the loop (user, 2026-10-31, Decisions.md D.058) - build a new one instead:
```fusion
int[] b = []
for x in a
    b.add(x * 2)        // fine - b is a new array
    // a.add(x)         // an error: a is being looped over
```

**Threads** (planned, Task 42): an array used by two or more threads gets a temporary service
(`files/Ownership.md` section 6, `files/Concurrency.md` 3.12).

**Use an array when:**
- you collect values in arrival order and read them back by position - readings from a
  sensor, lines of a file, the moves in a game
- the data is a fixed table - the days of a month, a 3 x 3 board, colour values
- speed and small memory matter (embedded devices): an array is the leanest sequence

**Don't use an array when:**
- items must be inserted or removed in the middle, or reordered - use a List
- you look things up by name or id - use a Map
- the items have different types - use a struct (or several arrays of one type each)

---

## 4. Lists

#### Today (built)

```fusion
List<int> numbers = [3, 1, 2]       // or List<int>() / List<int> numbers - empty
numbers.add(10)                     // at the end
numbers.insert(0, 7)                // anywhere - later items move up one position
numbers.removeAt(1)                 // anywhere - later items move down one position
numbers.sort()                      // or sortBy(function)
List<int> big = numbers.filter((int x) : x > 2)
List<int> part = numbers.slice(1, 2)            // a copy of 2 items from position 1
print("{@1} {@2}", numbers.len(), numbers.contains(10))
```

All methods: `add`, `insert`, `removeAt`, `remove`, `clear`, `len`, `contains`, `indexOf`,
`join`, `slice`, `sort`, `sortBy`, `filter`, `map`, `reduce` (`files/Builtins.md`).

#### Planned (user, 2026-10-27)

- **Adding many at once**: the items of another list, or a group of values
- **Capacity and buffer**: a list keeps room for more items than it holds (its capacity);
  when that room is used up, it grows by a buffer amount. Both can be set, so a list that
  will hold 10,000 items doesn't grow 10,000 times
- **A kept sort order**: a list can be told its order once (for example by name), and every
  item added goes into its sorted place
- **Changing it while looping**: the collection being looped over can't be changed inside the loop (user, 2026-10-31, Decisions.md D.058) - build a new one instead. Today a change inside `for x in list` is a
  ModifiedWhileLoopingError (never a skipped item)
- **Threads** (Task 42): a list or map used by two or more threads gets a temporary service;
  this setting picks its worker (`files/Concurrency.md` 3.12). Shared by default:

```toml
[collections]
threads = "shared"     # default: lists and maps share a pool of threads; "dedicated": each
                       # busy list / map gets its own thread
sharedThreads = 10    # default: the pool's size
```
- **Combining**: `List<int> all = a + b + c` - the same as arrays; for maps see section 5

**Use a List when:**
- items come and go anywhere - a to-do list, a playlist, players joining and leaving
- the order changes - sorting, moving an item up or down
- you filter, map or reduce a collection

**Don't use a List when:**
- you only ever add at the end and read by position - an array is simpler and leaner
- you search by a name or id - `indexOf` reads every item; a Map finds it at once
- the collection never changes after it's built - an array says so more clearly

---

#### Options, set in its set-up block (built - Task 32.14, tests/test_collection_options.py)

```fusion
List<string> names = [] {
    names.noDuplicates()       // adding a value it has: a DuplicateError
    names.noNull()             // adding null: a NullError
    names.readOnly()           // after the block, a change is a ReadOnlyError
}
```
A compile error where it can be seen (`names.add(...)` after the block), else an error while
running (the List passed to a function that changes it); a refused value is freed. A Map takes
`noNull()` and `readOnly()` (its keys never repeat already). Options anywhere else: an error.

## 5. Maps

**Built (Task 32.6, tests/test_map_collection.py):** a Map is a `Collection<Entry<K, V>>` - an
`Entry<K, V>` is its `key` and `value` (`Entry<string, int>("a", 1)`); `foreach k in m` gives
the keys, `foreach (Entry<string, int> e in m)` each key and value (D.096). `keys()` and
`values()` are **borrowed views** - `Collection<K>` / `Collection<V>` looking into the Map, no copy;
removing from one removes the entry, adding to one does nothing (false - a key needs a value);
`.toList()` gives a copy (D.095).

#### Today (built)

```fusion
Map<string, int> ages               // empty (or Map<string, int>())
ages["Alice"] = 30                  // adds the key
ages["Alice"] = 31                  // replaces the value
int a = ages["Alice"]               // a missing key is a KeyError
int z = ages.get("Zed", 0)          // or a default you choose
if ages.has("Bob")
    ages.remove("Bob")
for name in ages                    // keys, in the order they were added
    print(name)
```

All methods: `has`, `get`, `remove`, `keys`, `values`, `len`, `clear`. Also written
`Dictionary<K, V>`. Keys today: `string`, `int` or `char`.

#### Planned (user, 2026-10-27)

- **Values of any type**
- **Keys**: a non-empty constant string (never pooled - its text can't change under the map), or
  a whole number 0 or above (`byte`, `int`: 0, 140, 15661 - never a float, whose rounding
  makes equal-looking keys differ)
- **Your own hashing and key rules**: a map can bring its own hash function and its own
  key condition - for example "only non-empty strings" or "ints only"
- **No duplicate keys**: each key appears once (a List allows duplicates, a Map never)
- **Combining maps uses `add`, not `+`** (user, 2026-10-27): `ages.add(moreAges)` adds every
  key of another map. When a key is already there, a setting on the map decides - by default
  the incoming value **replaces** the old one ("Ann" from `moreAges` replaces "Ann" in
  `ages`)

**Use a Map when:**
- you look values up by a key - prices by product code, settings by name, users by id
- you count things - how often each word appears
- each key must appear once - adding the same key again replaces its value

**Don't use a Map when:**
- the order or position matters most - use an array or a List (a Map keeps the order keys
  were added, but you can't insert at a position or sort it)
- the keys are simply 0, 1, 2, ... - that is an array or a List
- you need several values per key - use `Map<string, List<string>>`

---

## 6. foreach - looping without changing (built - Task 32.4, tests/test_foreach.py)

**Built:** `foreach (string n in names)` or `foreach n in names` over an array, a List, a Map
(its keys) or a class implementing `Collection<T>`; changing the looped collection inside is a
compile error (any loop - D.058; an array's `add` / `pop` / replacing too - Task 45.7), a class of your own only with `[collections]
allowChangeWhileLooping = true`. A collection of your own gives a **new** `Iterator<T>` from
`iterator()` for each loop (`hasNext()`, `next()`), so a loop inside a loop over it works:

```fusion
class Team implements Collection<Person>
    Iterator<Person> function iterator() : TeamIterator(people)   // and the other Collection functions
class TeamIterator implements Iterator<Person>
    bool function hasNext() : at < people.len()
    Person function next() ...
```
**Built (32.6, tests/test_list_collection.py):** a List is a `Collection<T>` value -
`Collection<int> c = xs` holds the same List, every Collection function works on it, and
`c.iterator()` gives an `Iterator<int>`. **`hasNext()` is the way to check** - false when no
items are left, so `foreach` never fails. `next()` past the end (D.094): **null** for a string,
List, Map, object or enum - whatever the nullable settings say, null means no more items; a
primitive (`int`, `double` ...) can't be null: an IndexError, "check hasNext() first". Still
planned: an array (once on the heap - 45.10, its own implementation blocks removing an item)
and a Map as `Collection<T>` values - a Map as `Collection<Entry<K, V>>`, with `keys()` and
`values()` giving its keys and values as borrowed collections (D.092).

`foreach` goes over an array, list or map like `for x in`, but **promises not to change it**:
adding or removing items of that collection inside a `foreach` is a **compile error**. `continue`
skips to the next item and `break` leaves the loop.

```fusion
foreach (string item in names)       // the item's type is the collection's - also written
                                     // without brackets: foreach string item in names
    if item.isHidden()
        continue                     // skip this one
    if item.isLast()
        break                        // stop
    print(item)
    // names.add(x) or names.remove(x) here: a compile error
```

| | `for x in collection` | `foreach x in collection` |
|---|---|---|
| Adding / removing inside | **never** (D.058) - a compile error where seen, else ModifiedWhileLoopingError | always a **compile error** |
| Use it when | the loop needs the position (`i`) | reading only - the code says so |

**Future - the Collection interface** (user, 2026-10-27, with classes and interfaces, Task 32):
`foreach` works on anything that implements a `Collection` interface. Arrays, lists and maps
implement it; a class of your own can too, and decide its own rules - whether adding or
removing while looping is allowed, how it handles threads, or any special action that
collection needs. The compile error above is the rule of the built-in arrays, lists and
maps.

---

## 7. Choosing - examples

| Need | Use | Why |
|---|---|---|
| A temperature reading every second | array | added at the end, read by position |
| The 7 days of the week | array | fixed, never changes |
| A to-do list the user edits | List | insert, remove and reorder anywhere |
| A leaderboard kept in score order | List (kept sort order, planned) | every new score goes into its place |
| Phone numbers by name | Map | found by a key at once |
| Word counts in a book | Map | one counter per word |
| A shopping cart (items added and removed) | List | removed from anywhere |
| Lines read from a file | array | added in order, read back in order |
| Students per class | `Map<string, List<string>>` | a key with a group of values |

---

## 8. Copying a part, and the slice / splice confusion

Built: Task 45.5 - on every array and on Lists.

**Names (user, 2026-10-27):** `copyPart` - it says what it does; `slice` stays as quick
typing (familiar from JavaScript and Python). The same for the start-to-end form.

| Method | Gives |
|---|---|
| `copyPart(start, count)` (or `slice`) | a copy of count items from start; a count past the end stops at the end; a start outside is an IndexError |
| `copyPartAt(start, end)` (or `sliceAt`) | a copy from start to end, **both included**; an end past the end stops at the end; a start outside is an IndexError; start after end gives the items in reverse |

Positions count from **0**, as everywhere in Fusion (user, 2026-10-27): the first item is at
index 0. On `int[] someArray = [20, 30]`:

| Call | Gives |
|---|---|
| `sliceAt(0, 1)` | `[20, 30]` |
| `sliceAt(0, 2)` | `[20, 30]` - stops at the end |
| `sliceAt(1, 2)` | `[30]` |
| `sliceAt(2, 3)` | an IndexError - the start is outside |
| `sliceAt(1, 0)` | `[30, 20]` - start after end: reversed |

Both leave the original unchanged.

**Why slice and splice confuse people:** in JavaScript they differ by one letter but do
opposite things - `slice` copies a part and leaves the array alone; `splice` cuts items out
(and can insert new ones) and **changes** the array. Fusion has no `splice`. Clearer names,
to decide:

| Instead of | Suggested name | Reads as |
|---|---|---|
| `slice` (copy, original unchanged) | **`copyPart`** (chosen), `slice` as quick typing | "give me a copy of this part" |
| `splice` - removing a run of items | `removeRange(start, count)` | says it changes the list |
| `splice` - inserting several items | `insertAll(at, items)` | like `insert`, for many |
| `splice` - replacing a run | `replaceRange(start, count, items)` | says what it does |

The rule behind the names: a method that **changes** the collection says so with a verb
(`remove`, `insert`, `replace`); a method that **copies** returns a new one and leaves the
original alone.

---

## 8b. Arrays of 2 and 3 dimensions (Task 45.12, D.143, D.148-D.150)

To see it: [ArrayCube.html](ArrayCube.html) (open in a browser) shows which slots a part reaches, the
order `foreach` walks them, where each lies in the flat block, and what `expand` adds.

`int[2][3][4] cube` - 2 rows x 3 columns x 4 depth (sheets). One flat block (FLAT, D.144); `[arrays]
order` sets which index varies fastest in memory - `columns` (the default): rows fastest, so a loop
over depth -> columns -> rows reads the slots one after another.

| What | Written | Gives | Built |
|---|---|---|---|
| Declare | `int[2][3][4] cube`, `int[2],[3],[4] cube`, `int cube[2][3][4]`, `fixed int[2][3] f` | default slots | 45.12a |
| Where it lives | `int[2][3] m` / `int[2][3][4] cube` (local) | 1D and 2D on the stack (measured by `stackLimit`); 3D always on the heap - the same code, freed when its scope ends, never measured (D.154) | 45.12, 2026-11-21 |
| From values | `int[][] m = [[1, 2, 3], [4, 5, 6]]` | 2 x 3; rows of different lengths an error | 45.12a |
| One slot | `cube[1][2][3]`, `cube[1],[2],[3]` | read / write; each index checked (IndexError) | 45.12a |
| A written index outside | `m[1][3]` on `int[2][3] m` | a compile error | 45.12a |
| Sizes | `cube.rows`, `cube.columns`, `cube.depth` | 2, 3, 4; `depth` on 3 dimensions only | 45.12a |
| Length | `cube.length`, `m.length` | the outer dimension: 4 (depth), 3 (columns); `order = "rows"`: 2, 2 | 45.12a |
| One slot's length | `cube[1][2][3].length` | -1 (a string slot: the string's length) | 45.12b |
| A view's length | `cube[1].length`, `cube[][][3].length`, `cube[][2][1].length` | 4 (depth), 3 (columns), 2 (rows) | 45.12b |
| A view in a loop | `foreach (int v in cube[1][][3])` | borrowed: row 1 of sheet 3, one value per column | 45.12b |
| Loop the whole | `foreach (int[][] sheet in cube)` / `(int[] column in sheet)` / `(int v in column)` | depth -> columns -> rows; writes go to cube | 45.12b |
| A view to a variable | `int[][] s = cube[][][3]`, `int[] row = cube[1][2]` | a copy; objects shared, `byVal` copies them | 45.12b |
| An index a loop view fixes | `foreach (int v in cube[r][1])` | `r` read once, before the loop | 45.12b |
| Pass, that shape | `f(int[2][3] m)` - `f(m)` | the caller's array (writes reach it) | 45.12c |
| Pass, any size | `f(int[][] m)` - `f(m)`, `f(cube[1])` | its sizes passed hidden; a part copied (numbers) | 45.12c |
| A part to `int[]` | `total(m[1])`, `total(m[][2])` | a copy | 45.12c |
| Return | `int[2][3] function f()`; `int[][] function f()` | that shape; any size: an error (heap - later) | 45.12c |
| Compare | `a == b` | slot by slot, the same shape; a part: later | 45.12c |
| Give the whole to a new array | `int[2][3] n = m`, `int[][] n = byVal m` | the slots copied; `m` moved - can't be used after (D.025); `byVal` a deep copy, `m` stays; sizes agree or are taken from `m` | 45.12e |
| Replace the whole, same shape | `m = [[...]]`, `m = n`, `m = byVal n`, `m = make()` | the new slots made first, then the old freed and replaced; `m = n` moves `n`; fixed: an error | 45.12e part 3a |
| Replace the whole, another shape | `m = [[1, 2], [3, 4]]` on an `int[2][3]` | a plain array lives on the heap from its declaration (never expands); a growable one takes values or a stack array of any shape; fixed: an error | 45.12e part 3b |
| Grow | `int:[2][3][4] g`, `int[[2],[3],[4]] g`, `int:[][] g = [...]`; `g.expand(ROWS, 1)` | on the heap; a warning; it stays a cube, new slots the default | 45.12d |
| Grow by a number | `g.expand(0, 1)` | an error - the Collections library | - |
| Storage | `m.setStorage(FLAT)` / `null`, right after the declaration (D.147) | one block - the default; `RECT` comes later (D.164) | 45.15 |
| Jagged | `int:[][] j = [[1], [2, 3, 4]]` then `j.setStorage(JAGG)` | rows of their own length: `j.rows`, `j[r].columns`, `j.columns` 0, `j[r].add(v)`, `j.add(row)`; foreach by `[arrays] order` (columns first, short rows skipped); 2 dimensions (D.153, D.163) | 45.15 |
| To a List | `m.toList()`, `cube.toList()`, `m[1].toList()` | a List of Lists, the outer dimension first; a copy; a null slot skipped, a column all null an empty List (D.152) | 45.11, 45.11c |
| To CSV | `m.toCSV()`, `m.toCSV(";", "#", "\n")` | a line per row; 3 dimensions the sheets side by side split by `#`; CSV quoting; a null slot an empty field ([arrays] csvManyDimensions) | 45.11b, D.151 |
| Grow while looping | `foreach (int[] c in g)` ... `g.expand(ROWS, 1)` | a compile error (D.058) | 45.12d |
| 4 dimensions | `int[2][3][4][5]` | a compile error - the Collections library | - |

## 8c. Every array form - a truth table (Task 45.6, 2026-11-22)

Each cell was compiled and run (Rule 4c) - **yes** works, **error** is a compile error that says what to
do instead, **later** is a compile error "comes later". The forms, as declared:
- **plain** `int[] a = [1, 2, 3]`, **fixed** `fixed int[3] a`, **growable** `int:[] a` (also `int[[]] a`)
- **2D** `int[2][3] m`, **3D** `int[2][3][4] c`, **growable 2D / 3D** `int:[][] g` (also `int[[2],[3]] g`)
- **jagged** `int:[][] j` then `j.setStorage(JAGG)` - rows of their own length (2 dimensions)

| What | plain | fixed | growable | 2D | 3D | growable 2D / 3D | jagged |
|---|---|---|---|---|---|---|---|
| Lives on | stack; heap once replaced by another size (45.10) | stack | heap | stack; heap once given another shape | heap (D.154) | heap | heap - a block of rows |
| Read / write a slot, each index checked | yes | yes | yes | yes | yes | yes | yes - IndexError only on `j[x][y]` (D.163) |
| `length` | yes | yes | yes | yes - the outer first ([arrays] order) | yes | yes | error - `j.rows`, `j[r].columns` |
| `rows`, `columns`, `depth` | - | - | - | yes | yes | yes | `j.rows`; `j.columns` 0; `j[r].columns` |
| Replace the whole, same size | yes | error - fixed | yes | yes | yes | yes | yes |
| Replace the whole, another size | yes (to the heap) | error - fixed | yes | yes (to the heap) | yes | yes | yes |
| `add`, `removeLast` / `pop` | error - declare `int:[]` | error | yes | error - `expand` on a growable one | error | error - `expand` | `j.add(row)`, `j[r].add(v)`, `j.removeLast()` (a row) |
| `expand(ROWS / COLUMNS / DEPTH, n)` | - | - | - | error - only a growable one | error | yes, a warning | error |
| Given whole to a new one (`b = a` moves) | yes | yes | yes | yes | yes | later | later |
| `byVal` copy | yes | yes | yes | yes | yes | later | later |
| Passed to a parameter (`int[]` / `int[][]`) | yes | yes | yes | yes | yes | yes | later - one row passes to `int[]` |
| `==` | yes | yes | yes | yes - the same shape | yes | later | later |
| `toList()` | yes | yes | yes | yes - a List of Lists | yes | yes | later |
| `toCSV()` | yes | yes | yes | yes | yes - sheets side by side | yes | later |
| `foreach` | yes | yes | yes | yes - [arrays] order | yes | yes | yes - columns first (short rows skipped) or rows |
| `copyPart` / `slice`, `a + b` | yes | yes | yes | error - one dimension only | error | error | later |
| `setStorage(FLAT / null)` | error - 2 or 3 dimensions | error | error | yes (the default) | yes | yes | - |
| `setStorage(RECT)` | - | - | - | later (D.164) | later | later | - |

Found while building this table and fixed: `a.toList().len()` on 2 or 3 dimensions freed the new List twice;
`a.add(4)` on a plain array said "only structs have fields".

## 9. Decisions log

| Date | Decision |
|---|---|
| 2026-10-27 | Arrays, lists and maps are never null: empty when declared (`files/Nullable_Values.md`) |
| 2026-10-27 | Arrays grow and shrink at the end only (add one, combine arrays); an item never moves position. Lists add, remove and reorder anywhere |
| 2026-10-27 | `int numbers[]` and `int[] numbers` declare an empty array - waits for growing arrays (files/FEATURES.md Task 45) |
| 2026-10-27 | Lists: capacity and a growth buffer, and a kept sort order (planned) |
| 2026-10-27 | Taking a part (`slice`) gives a copy; the original is unchanged |
| 2026-10-27 | `a + b` combines arrays; `removeLast()` removes the last item, `pop()` is quick typing for it |
| 2026-10-27 | `slice(start, count)`: a count past the end stops at the end; a start outside is an IndexError. `sliceAt(start, end)`: start after end gives the items in reverse |
| 2026-10-27 | Arrays: changing at the end while looping is allowed (the loop sees the new length). Lists / maps: a setting allows it; otherwise ModifiedWhileLoopingError - **replaced 2026-10-31**: never changed while looped over; build a new one (D.058) |
| 2026-10-27 | Threads: an array's add / remove at the end takes an implicit atomic lock; a list or map is served by a shared or dedicated thread - **replaced 2026-10-31**: a temporary service; the setting picks its worker (D.057) |
| 2026-10-27 | `copyPart` / `copyPartAt` (with `slice` / `sliceAt` as quick typing); `end` included; an end past the end stops there; a start outside is an IndexError |
| 2026-10-27 | Combine any number at once: `A + B + C + D` - arrays and lists, all of the same type. Maps use `add(otherMap)`, not `+`; a setting on the map decides a key already there - replace by default |
| 2026-10-27 | Positions count from 0 in `copyPart` / `copyPartAt` too |
| 2026-10-27 | Duplicates: arrays and lists allow them; a map's keys never repeat |
| 2026-10-27 | `foreach (string item in names)` - the item's type is the collection's. Future: a `Collection` interface (Task 32) - arrays, lists, maps and your own classes implement it, and a class decides its own looping / thread rules |
| 2026-10-27 | `foreach` over arrays, lists and maps: adding / removing inside is a compile error; `continue` and `break` allowed |
| 2026-10-27 | Lists / maps and threads: shared by default, `[collections] threads = "shared"`, `shared_threads = 10` |
| 2026-10-29 | `toList(copy = true)` on a List and an array; setting an array / List / Map to null is an error unless its nullable setting allows it |
| 2026-10-29 | Arrays, Lists and Maps are references (shared) in normal code - a variable, parameter, class field, element - and copied inside a struct; `byVal` copies in normal code, `byRef` shares in a struct field. Never null, just empty |
| 2026-10-31 | Planned (Task 48): Lists and Maps move on assignment, `byVal` copies, reading an element or passing borrows; a struct's collection only lends itself (files/Ownership.md) |
| 2026-11-01 | A Map is a Collection<Entry<K, V>>; keys() / values() are borrowed views (.toList() copies); foreach k in m gives keys, typed Entry gives entries (D.092, D.095, D.096) |
| 2026-11-01 | `Iterator<T>` (hasNext, next); a collection gives a new one from `iterator()` for each loop; foreach needs it; arrays, Lists and Maps implement Collection<T> and Iterator<T> - an array's own implementation blocks remove (D.089, D.090) |
| 2026-10-31 | Planned (47.5): `fixed(n)` - only the size is limited, the values may change (`const`: nothing changes); lower fine, never higher; starts empty, grows up to it, memory reserved once |
| 2026-10-27 | Map values of any type; keys a non-empty fixed string or a whole number 0 or above; a map may bring its own hashing and key rules |
