[< 030 Types](030-Types.md) | [Index](index.md) | [032 Strings >](032-Strings.md) <!-- nav -->

# 031 Arrays

The design behind them (arrays, Lists, Maps): [files/Arrays.md](../Arrays.md) - its section 8c is the truth
table of every array form and what each can do, every cell compiled and run (Task 45.6).

## The three forms (D.141)

```
int[] scores = [10, 20, 30]       // plain - the size from the values
float[3] buffer                   // plain - 3 zeros
int[] none                        // plain - empty, size 0 (Task 45.2)
int numbers[] = [1, 2]            // the same as int[] numbers - brackets after the name
fixed int[3] podium = [3, 1, 2]   // fixed - never another size (Task 45.14)
int:[] xs                         // growable - also int[[]] xs, int xs[[]] (Task 45.3)
int:[10] ys                       // growable, 10 slots made ahead - length 10 (45.3b)

scores[0] = 99                    // every index checked - outside is an IndexError (Task 27.1)
scores.length                     // also scores.len, len(scores), Array.length(scores) (45.1, D.142)
xs.add(4)                         // only a growable array grows - at its end
int last = xs.removeLast()        // gives the item back (pop() the same); empty: an IndexError
```

- **plain:** keeps its size until it is replaced as a whole - `scores = [1, 2]`, `scores = make()`; replaced
  by another size it lives on the heap (a counted block, like a List) and still acts as an array (45.10)
- **fixed:** the size is set once - written, from the values, or from `f()` while running; replacing it is an
  error, setting its slots is fine
- **growable:** on the heap; `add`, `removeLast` / `pop` at the end only - an item never moves position
- Never null (D.138); an object slot may be null - `Car[] cars = [car1, null]`, `cars[0] = null` frees the
  object (D.140)
- Where it lives: a plain or fixed array on the stack, measured in bytes - above `[arrays] stackWarn` (16KB) a
  warning, above `stackLimit` (64KB) a compile error (45.13, D.145); `setBufferType` / `setSize` are an error
  "not built yet" (D.146, after self-hosting)

## Parameters and results

```
int function sum(int[] values)     // any size - its length passed hidden
int function middle(int[3] trio)   // exactly 3, checked while compiling
int[3] function podium() : [3, 1, 2]
int[] function make(int n)         // any size - on the heap (45.10)

int total = sum(scores)            // the caller's array - changes reach it, nothing copied
int[3] a = podium()                // copied in; a = podium() replaces its slots
```

- Element types must match exactly - an `int[]` isn't a `float[]`
- A returned array can be stored, assigned, indexed or returned; passed straight on, keep it in a variable first

## Copying, combining, parts

```
int[3] b = a                       // moves: the slots copied, a can't be used after (D.025, 45.12e)
int[3] c = byVal a                 // a copy - a stays usable
int[] all = a + b + c              // a new array, on the heap (45.4)
int[] part = scores.copyPart(1, 2) // 2 items from 1 - a copy (slice the same); copyPartAt(1, 2) from 1 to 2 (45.5)
List<int> l = scores.toList()      // a List copy (32.10a); a null object slot skipped (D.152)
string csv = scores.toCSV()        // "10,20,30" (45.11b)
```

- Not changed while looped over: `add`, `removeLast` or replacing it inside a loop over it is a compile
  error, also through a function or method; setting a slot is fine (45.7, D.058)

## Two and three dimensions (Task 45.12, D.143, D.148-D.150)

```
int[2][3][4] cube                  // rows x columns x depth - also int[2],[3],[4] cube, int cube[2][3][4]
int[][] m = [[1, 2, 3], [4, 5, 6]] // sizes from the values
cube[1][2][3] = 9                  // each index checked against its own size
m.rows; m.columns; cube.depth      // 2, 3, 4
cube[1]                            // a view - an index left out means all of it (D.149)
foreach (int[][] sheet in cube)    // the outer dimension first - [arrays] order
int:[][] g = [[1, 2], [3, 4]]      // growable - g.expand(ROWS, 1) (a warning: every slot copied)
```

- `[arrays] order` (D.148): `"columns"` (default) depth -> columns -> rows; `"rows"` rows -> columns -> depth;
  `"depthRows"` depth -> rows -> columns - loops, `length`, `toList` and the memory layout follow it
- 1D and 2D live on the stack, a 3D array always on the heap (D.154)
- Parameters `int[2][3] m` (that shape) or `int[][] m` (any - its sizes passed hidden); `==` on the same
  shape; `toList` a List of Lists; `toCSV` the sheets side by side (D.151)
- More than 3 dimensions and `expand(0, n)`: the Collections library

## Storage (Task 45.15, D.144, D.153, D.163, D.164)

```
int[2][3] m
m.setStorage(FLAT)                 // right after the declaration, or in its set-up block (D.147)
int:[][] j = [[1], [2, 3, 4]]
j.setStorage(JAGG)                 // jagged: rows of their own length - a growable array of 2 dimensions
j.rows; j[1].columns; j.columns    // 2, 3, 0 - no row given
j[0].add(5); j.add([7, 8])         // one row grows; a new row
```

- `[arrays] storage = "flat"` - one block, the default; `RECT` comes later (D.164); JAGG per array only
- A jagged array: only `j[x][y]` outside a row is an IndexError; `foreach` columns first by default (each a
  new array from the rows long enough for it) or rows; a row passes to an `int[]` parameter
- On a jagged array later: passing the whole, copying it, `==`, `toList`, `toCSV`, `j[][1]`, 3 dimensions

## Not built yet

- An array size from a variable - `int[n]`; only a number written in the code
- Lambdas and function types returning arrays
- Threads: an array used by two or more threads gets a temporary service (Task 42, files/Ownership.md 6)

[< 030 Types](030-Types.md) | [Index](index.md) | [032 Strings >](032-Strings.md) <!-- nav -->
