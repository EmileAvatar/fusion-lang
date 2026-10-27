# Single values, arrays, lists and maps

The four ways Fusion holds data: what each can do, when to use it, and when not to.
Decisions by the user, 2026-10-27. Status marks: **built** (works today) and **planned**
(designed, scheduled in `FEATURES.md`). Every built-in method is listed in
`files/Builtins.md`. Null rules: `Nullable_Values.md`.

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
| Copying `b = a` | a copy | an independent copy | an independent copy | an independent copy |
| Cost of adding | - | cheap at the end | cheap at the end, slower in the middle (later items move up) | cheap |
| Status | built | built (fixed size); growing planned | built | built |

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

The size is fixed when the array is made. `int[] numbers` with no size or values is an error
today ("must specify a size ... or be initialized").

#### Planned: arrays that grow at the end (user, 2026-10-27)

An array grows and shrinks **only at its end**. Nothing is inserted in the middle, so no item
ever moves to another position.

```fusion
int numbers[]              // [] - empty, length 0 (also written int[] numbers)
numbers.add(4)             // [4]     - index 0, length 1
numbers.add(6)             // [4, 6]
numbers.removeLast()       // [4]     (pop() is the same - quick typing)
int[] more = numbers + [7, 8]        // a + b: b's items after a's -> [4, 7, 8]
int[] all = a + b + c + d            // any number at once - all of the same type
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

**Looping while it changes** (planned): adding or removing at the end inside `for x in numbers`
is allowed - the loop sees the new length, so no temporary copy is needed.

**Threads** (planned, Task 42): adding or removing at the end is thread-safe by itself - an
implicit atomic lock (`Concurrency.md` 3.12).

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
- **Changing it while looping**: today adding or removing inside `for x in list` is a
  ModifiedWhileLoopingError (never a skipped item). A setting will allow it for a list
  (or a map) that needs it - so no temporary copy is needed
- **Threads** (Task 42): a list or map is served by a shared or its own thread for adding,
  reading and removing (`Concurrency.md` 3.12). Shared by default:

```toml
[collections]
threads = "shared"     # default: lists and maps share a pool of threads; "dedicated": each
                       # busy list / map gets its own thread
shared_threads = 10    # default: the pool's size
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

## 5. Maps

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
- **Keys**: a non-empty fixed string (never pooled - its text can't change under the map), or
  a whole number 0 or above (`byte`, `int`: 0, 140, 15661 - never a float, whose rounding
  makes equal-looking keys differ)
- **Your own hashing and key rules**: a map can bring its own hash function and its own
  key condition - for example "only non-empty strings" or "ints only"
- **Combining**: `Map<string, int> all = a + b + c` (same types). **Open:** when two maps have
  the same key - the later one wins (as Python's `a | b` and JavaScript's spread), or an
  error?

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

## 6. foreach - looping without changing (planned, user 2026-10-27)

`foreach` goes over an array, list or map like `for x in`, but **promises not to change it**:
adding or removing items of that collection inside a `foreach` is a **compile error**. `continue`
skips to the next item and `break` leaves the loop.

```fusion
foreach item in collection           // also written: foreach (item in collection) { ... }
    if item.isHidden()
        continue                     // skip this one
    if item.isLast()
        break                        // stop
    print(item)
    // collection.add(x) or collection.remove(x) here: a compile error
```

| | `for x in collection` | `foreach x in collection` |
|---|---|---|
| Adding / removing inside | arrays: allowed (the loop sees the new length); lists / maps: a setting, otherwise ModifiedWhileLoopingError at run time | always a **compile error** |
| Use it when | the loop must change the collection | reading only - the code says so, and the compiler checks it |

(`var` in `foreach (var item in collection)`, as in C#, waits for type inference; until then
the item's type comes from the collection, as in `for x in`.)

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

**Names (user, 2026-10-27):** `copyPart` - it says what it does; `slice` stays as quick
typing (familiar from JavaScript and Python). The same for the start-to-end form.

| Method | Gives |
|---|---|
| `copyPart(start, count)` (or `slice`) | a copy of count items from start; a count past the end stops at the end; a start outside is an IndexError |
| `copyPartAt(start, end)` (or `sliceAt`) | a copy from start to end, **both included**; an end past the end stops at the end; a start outside is an IndexError; start after end gives the items in reverse |

The user's examples (2026-10-27) on `int[] someArray = [20, 30]`:

| Call | Gives |
|---|---|
| `sliceAt(1, 2)` | `[20, 30]` |
| `sliceAt(1, 3)` | `[20, 30]` - stops at the end |
| `sliceAt(2, 3)` | `[30]` |
| `sliceAt(3, 4)` | an IndexError - the start is outside |

**Open:** these examples count from **1** (position 1 is 20). Everything else in Fusion
counts from **0**, as C, Java, C#, JavaScript and Python do - `someArray[0]` is 20,
`xs.insert(0, ...)`, `slice(0, 2)`. Counted from 0 the same calls would be `sliceAt(0, 1)`
-> `[20, 30]`, `sliceAt(0, 2)` -> `[20, 30]`, `sliceAt(1, 2)` -> `[30]`, `sliceAt(2, 3)` ->
IndexError. To confirm which.

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

## 9. Decisions log

| Date | Decision |
|---|---|
| 2026-10-27 | Arrays, lists and maps are never null: empty when declared (`Nullable_Values.md`) |
| 2026-10-27 | Arrays grow and shrink at the end only (add one, combine arrays); an item never moves position. Lists add, remove and reorder anywhere |
| 2026-10-27 | `int numbers[]` and `int[] numbers` declare an empty array - waits for growing arrays (FEATURES.md Task 45) |
| 2026-10-27 | Lists: capacity and a growth buffer, and a kept sort order (planned) |
| 2026-10-27 | Taking a part (`slice`) gives a copy; the original is unchanged |
| 2026-10-27 | `a + b` combines arrays; `removeLast()` removes the last item, `pop()` is quick typing for it |
| 2026-10-27 | `slice(start, count)`: a count past the end stops at the end; a start outside is an IndexError. `sliceAt(start, end)`: start after end gives the items in reverse |
| 2026-10-27 | Arrays: changing at the end while looping is allowed (the loop sees the new length). Lists / maps: a setting allows it; otherwise ModifiedWhileLoopingError |
| 2026-10-27 | Threads: an array's add / remove at the end takes an implicit atomic lock; a list or map is served by a shared or dedicated thread |
| 2026-10-27 | `copyPart` / `copyPartAt` (with `slice` / `sliceAt` as quick typing); `end` included; an end past the end stops there; a start outside is an IndexError |
| 2026-10-27 | Combine any number at once: `A + B + C + D` - arrays, lists and maps, all of the same type |
| 2026-10-27 | `foreach` over arrays, lists and maps: adding / removing inside is a compile error; `continue` and `break` allowed |
| 2026-10-27 | Lists / maps and threads: shared by default, `[collections] threads = "shared"`, `shared_threads = 10` |
| 2026-10-27 | Map values of any type; keys a non-empty fixed string or a whole number 0 or above; a map may bring its own hashing and key rules |
