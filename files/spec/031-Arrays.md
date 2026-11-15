[< 030 Types](030-Types.md) | [Index](index.md) | [032 Strings >](032-Strings.md) <!-- nav -->

# 031 Arrays

The design behind them (arrays, Lists, Maps, truth tables): [files/Arrays.md](../Arrays.md).

## Arrays

Description: Fixed-size, homogeneous collections of a single element type.

```
int[] scores = [10, 20, 30]      // size inferred from the literal
float[3] buffer                   // explicit size, zero-initialized (no literal needed)
int[3] three = [1, 2, 3]          // explicit size + literal (must agree)
int[] none                        // empty - size 0 (Task 45.2)
int numbers[] = [1, 2]            // the same as int[] numbers - brackets after the name (kept, user 2026-11-15)
fixed int[3] podium = [3, 1, 2]   // fixed - never another size (Task 45.14, D.141)
Array.length(scores)              // the Array class - the same as scores.length (Task 45.1, D.142)

scores[0]                         // read
scores[0] = 99                    // write an element
int count = len(scores)           // size, as a builtin function call
```

**Implemented (Task 9 v1):** local array variables, declared with an explicit size
(`int[N]`), an initializer (`int[] x = [...]`, size inferred), or both (which must agree).
Reading and writing individual elements (`arr[i]`, `arr[i] = value`). `len(arr)` as a
builtin - since size is always known at compile time, `len(arr)` compiles directly to that
size as a literal, not a runtime call. `const int[] arr = [...]` works the same as scalar
`const` - the array and its elements become immutable.

**Array parameters (implemented, Task 18.1.2):**

```
int function sum(int[] values)     // any size - len(values) is its actual length
int function middle(int[3] trio)   // exactly 3 elements, checked at compile time

int total = sum(scores)            // pass an array variable
int other = sum([7, 8])            // or an array literal directly
```

* Arrays are **passed by reference** - the function works on the caller's array, so element
  changes are visible to the caller, and nothing is copied
* `int[]` accepts an array of any size. C loses an array's length when it's passed, so the
  compiler passes the length alongside it as a hidden parameter, and `len(values)` reads it
* `int[N]` accepts only an array whose size is known at compile time to be exactly N
* Element types must match exactly - an `int[]` can't be passed as a `float[]` (no numeric
  promotion, since the function reads the caller's memory directly)
* A `const` array can't be passed (the function could change it - a read-only parameter
  form doesn't exist yet); array parameters can't have default values
* An array can only be initialized from an array literal - `int[] b = a` is an error
  (whether that should copy or share `a` is undecided) - or from an array a function
  returns (below)

**Array return values (implemented, Task 18.2.4):**

```
int[3] function podium() : [3, 1, 2]
Point[2] function ends(int size)
    return [Point(0, 0), Point(size, size)]

int[3] a = podium()        // copied into a new array
a = podium()               // replaces a's elements
int top = podium()[0]      // indexed directly
team.scores = podium()     // an array field too
```

* A sized return type (`int[3]`) gives exactly that many; `int[]` gives an array of any size,
  on the heap (Task 45.10, D.141): `int[] function make(int n)`
* `return` takes an array literal of exactly that size (numbers may be promoted), or any
  array of exactly the same type and size - a variable, parameter, struct field, or another
  call; it is copied
* A returned array can be stored, assigned to an array (or array field), indexed, returned
  again, or ignored. Passing it straight to another function, `len()`, or `print` is an
  error - store it in a variable first
* Copying needs exactly the same element type and size (no int -> float promotion), and a
  `const` array can't be set from a call
* Not yet: lambdas and function types returning arrays, and using such a function as a value
* Under the hood, C can't return an array, so it's returned inside a hidden struct and
  copied out

**Not yet implemented (see files/taskSummary2.md Task 9 for the full list and reasoning):**
- Arrays of 2 and 3 dimensions - built (Task 45.12a, D.143, D.148): `int[2][3][4] cube` (also
  `int[2],[3],[4]`, `int cube[2][3][4]`), `int[][] m = [[1, 2, 3], [4, 5, 6]]`; `cube[1][2][3]` /
  `cube[1],[2],[3]`, each index checked; `rows`, `columns`, `depth`, `length` (the outer first); one flat
  block on the stack laid out in `[arrays] order`. Views (built - 45.12b, D.149): `cube[1]`, `cube[][2][1]`;
  `foreach` the outer dimension first, its variable a borrowed view; a view to a variable a copy;
  `length` the outer open dimension, -1 on one slot. Functions (built - 45.12c): `int[2][3] m` / `int[][] m`
  parameters (any size: its sizes passed hidden), a part passed as a copy, `int[2][3] function f()`,
  `==` on the same shape. Growable (built - 45.12d): `int:[2][3] g` / `int[[2],[3]] g` / `int:[][] g = [...]`
  on the heap, `g.expand(ROWS / COLUMNS / DEPTH, n)` (the built-in enum `Dimension`) with a warning; more than
  3 and `expand(0, n)`: the Collections library
- An array size given as anything other than an integer literal (`int[n]` where `n` is a
  variable is not supported; only `int[5]`-style literal sizes are)
- Whole-array reassignment - built since Task 45.10 (D.141): `arr = [4, 5]` or `arr = make()` replaces
  it, another size too; such an array lives on the heap (a counted block, like a List) and still
  acts as an array - no `add`, an object slot may be null. A `fixed` one keeps its size
- Size on the stack - built (Task 45.13, D.145): a plain or fixed array (or a struct holding one) above
  `[arrays] stackWarn` (16KB) is a warning, above `stackLimit` (64KB) a compile error - in bytes;
  `setBufferType` / `setSize` are an error "not built yet" (D.146, after self-hosting)
- Not changed while looped over - built (Task 45.7, D.058): `add`, `removeLast` / `pop` or replacing the
  array inside a loop over it is a compile error (also through a function or a method); setting an
  item is allowed
- Copying a part - built (Task 45.5, D.046): `copyPart(start, count)` / `copyPartAt(start, end)` (`slice` /
  `sliceAt`) on every array and List; past the end stops there, a start outside is an IndexError,
  copyPartAt includes its end and reverses when start > end
- Combining - built (Task 45.4, D.047): `a + b + c` makes a new array of one type, on the heap; two
  Lists make a new List; an array and a List don't mix (`toList()` first)
- Arrays that grow - built (Task 45.3, D.141): `int:[] xs` / `int[[]] xs` / `int xs[[]]` - `add`,
  `removeLast` (`pop`) at the end - it gives the item back; an empty one's `removeLast` an IndexError;
  `int:[10] xs` / `int[[10]] xs` has 10 slots made ahead (length 10, as `int[10]` - 45.3b). Up to 3 dimensions -
  planned (45.12, D.143)
- Bounds checking - built since then: every index is checked, outside the array is an
  IndexError (Task 27.1)
- `arr.length` / `arr.len`, with or without brackets - built (Task 30.8): the same as
  `len(arr)`, also on strings, bytes, lists and maps. An array is never null (D.138), so it needs
  no `?.`; a slot of an object array may be null - `Car[] cars = [car1, null]`, `cars[0] = null`
  frees the object (D.140, Task 52.11)

[< 030 Types](030-Types.md) | [Index](index.md) | [032 Strings >](032-Strings.md) <!-- nav -->
