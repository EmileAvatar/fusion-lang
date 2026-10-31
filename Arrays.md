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

The counting (Object_Lifetime.md section 5) frees a List or Map when its last holder lets go.
**Arrays** follow the same rule once they live on the heap and know their own length (Task
45); until then an array keeps today's behaviour (fixed size, copied).

**Planned - moving by default (Task 48, user 2026-10-31 - Ownership.md):** the table above
is today's rule. With Task 48 `List<int> b = a` **moves** (a is no longer usable), `byVal`
copies, and code that reads an element or passes a List borrows it. A collection inside a
struct only lends itself - `List<string> xs = order.items` is a borrow, never a move
(Ownership.md truth tables 1, 2). Arrays follow the same rule once on the heap (45.10). A
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

**Looping:** the collection being looped over can't be changed inside the loop (user, 2026-10-31, Decisions.md D.058) - build a new one instead:
```fusion
int[] b = []
for x in a
    b.add(x * 2)        // fine - b is a new array
    // a.add(x)         // an error: a is being looped over
```

**Threads** (planned, Task 42): an array used by two or more threads gets a temporary service
(`Ownership.md` section 6, `Concurrency.md` 3.12).

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
  this setting picks its worker (`Concurrency.md` 3.12). Shared by default:

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

## 6. foreach - looping without changing (planned, user 2026-10-27)

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
| 2026-10-31 | Planned (Task 48): Lists and Maps move on assignment, `byVal` copies, reading an element or passing borrows; a struct's collection only lends itself (Ownership.md) |
| 2026-10-31 | Planned (47.5): `fixed(n)` - only the size is limited, the values may change (`const`: nothing changes); lower fine, never higher; starts empty, grows up to it, memory reserved once |
| 2026-10-27 | Map values of any type; keys a non-empty fixed string or a whole number 0 or above; a map may bring its own hashing and key rules |
