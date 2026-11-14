[< 030 Types](030-Types.md) | [Index](index.md) | [032 Strings >](032-Strings.md) <!-- nav -->

# 031 Arrays

The design behind them (arrays, Lists, Maps, truth tables): [files/Arrays.md](../Arrays.md).

## Arrays

Description: Fixed-size, homogeneous collections of a single element type.

```
int[] scores = [10, 20, 30]      // size inferred from the literal
float[3] buffer                   // explicit size, zero-initialized (no literal needed)
int[3] fixed = [1, 2, 3]          // explicit size + literal (must agree)

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

* The return type needs a fixed size (`int[3]`, not `int[]`) - the caller must know how big
  the array is
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
- Multi-dimensional arrays (`int[][]`)
- An array size given as anything other than an integer literal (`int[n]` where `n` is a
  variable is not supported; only `int[5]`-style literal sizes are)
- Whole-array reassignment after declaration (`arr = [4, 5, 6]`, `arr = other`) - only
  per-element assignment, or assigning an array a function returns (`arr = make()`), is
  supported, since a plain C array isn't reassignable that way
- Dynamic/resizable arrays (no `malloc`-backed growth yet - fixed-size only)
- Bounds checking - built since then: every index is checked, outside the array is an
  IndexError (Task 27.1)
- `arr.length` / `arr.len`, with or without brackets - built (Task 30.8): the same as
  `len(arr)`, also on strings, bytes, lists and maps. An array is never null (D.138), so it needs
  no `?.`; a slot of an object array may be null - `Car[] cars = [car1, null]`, `cars[0] = null`
  frees the object (D.140, Task 52.11)

[< 030 Types](030-Types.md) | [Index](index.md) | [032 Strings >](032-Strings.md) <!-- nav -->
