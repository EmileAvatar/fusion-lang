# Fusion Syntax Reference - what works today

A showcase: one short example per **implemented** feature. Every ` ```fusion ` block is a
complete program that `python check.py` compiles and runs, so this file can't drift from the
compiler. The marker above each block (`<!-- example: name | task: N | folder: X -->`) names the program
`python check.py --build-examples` writes to `examples/X/` (a numbered topic folder, such as `01_basics`). Planned features are listed in `files/FEATURES.md`; the full design is in
`files/fusion-language-spec.md`.

When a feature ships, add its example here (Auto-Update Policy in `CLAUDE.md`).

---

#### Hello, functions and the three block styles

<!-- example: syntax_functions_and_blocks | task: 01-04 | folder: 01_basics -->
```fusion
// Return type first. One-line functions use ':'
int function add(int a, int b) : a + b

// 1. Indentation
int function bigger(int a, int b)
    if a > b
        return a
    return b

// 2. Braces
int function smaller(int a, int b) {
    if a < b {
        return a
    }
    return b
}

// 3. End keywords
void function main()
    print("Hello, Fusion!")
    print("{@1} {@2} {@3}", add(2, 3), bigger(4, 9), smaller(4, 9))
End function
```

`print` always ends the line it prints (there is no separate `println` yet).

#### Variables, constants, control flow

<!-- example: syntax_variables_and_control_flow | task: 08 | folder: 01_basics -->
```fusion
void function main()
    int count = 0
    float price = 2.5
    bool ready = true
    char grade = 'A'
    const int LIMIT = 3

    while count < LIMIT
        count = count + 1
    for i in range(0, 10, 2)
        if i == 4
            continue
        if i == 8
            break
        print("i = {i}")
    if ready and not (price > 5.0)
        print("count {count}, grade {grade}, ready {ready}")   // a bool prints as true / false
```

#### Ranges: `1...10` in a loop and in a match

<!-- example: syntax_ranges | task: 33.2f | folder: 01_basics -->
```fusion
string function grade(int score)
    match score
        case 90...100                       // both ends included
            return "A"
        case 80...89, 79
            return "B"
        else
            return "C"

void function main()
    int total = 0
    for i in 1...10                         // 1 to 10 - the same as range(1, 11)
        total = total + i
    print("{total}")                        // 55
    int n = 3
    for i in 0...n - 1                      // any whole-number values
        print("{i}")                        // 0 1 2
    for i in 10...0 step -5                 // a step; a negative one counts down
        print("{i}")                        // 10 5 0
    char c = 'q'
    string kind = match c
        'a'...'z' : "lower"                 // characters too
        'A'...'Z' : "upper"
        else : "other"
    print("{@1} {@2}", grade(95), kind)     // A lower
```
`a...b` counts from a to b, both ends included - `range(a, b + 1)`; the end and the step are worked out once,
before the first turn. `step` (D.170) - a word only after a range, so a variable may still be called step: only the
values within the range run - `0...13 step 5` gives 0 5 10, with a warning that 5 doesn't land on 13
(`[ranges] strictStep = true` makes it an error); a negative step counts down (`10...0 step -2`). A step of 0 is a
compile error when written, a RangeError while running when it comes from a value - a loop that never ends can't be
made. Numbers written against the step's way (`10...1`, `1...10 step -2`) are an error that says what to write;
from values such a range runs no turns, as `range` does. `range(a, b, step)` leaves b out and counts down with a
negative step. Decimal and money ranges come with Task 47.6. A case `0...9` matches whole numbers or characters
from its first end to its last; it may not overlap another case.

#### Module variables and constants: shared by a module's functions

<!-- example: syntax_module_variables | task: 44.1 | folder: 01_basics -->
```fusion
const int LIMIT = 3                       // a module constant
int count = 0                             // a module variable - every function sees it
List<string> log = []                     // freed when the program ends

void function note(string what)
    count = count + 1
    log.add(what)

void function main()
    for i in range(0, LIMIT)
        note("step {i}")
    print("{count} steps: {@1}", log.join(", "))
```
They are set in the order written, before `main`'s own code; an initializer may use the
functions and the module variables above it. `public` lets other modules use one
(`stats.total`). A name inside a function can't hide a module variable. `[modules] variables =
false` in `fusion.toml` turns module variables off (constants stay allowed).

#### Default parameters and named arguments

<!-- example: syntax_defaults_and_named_args | task: 18.2.2 | folder: 02_functions -->
```fusion
void function greet(string name = "World", int times = 1)
    for i in range(0, times)
        print("Hello, {name}!")

int function sub(int a, int b) : a - b

void function main()
    greet()                      // defaults filled in
    greet("Fusion", 2)
    greet(times = 1)             // named: skip any parameter with a default
    print("{@1}", sub(b = 5, a = 3))   // any order, unnamed ones first
```

#### Interpolation and `{@N}` placeholders

<!-- example: syntax_interpolation | task: 18.2.2b | folder: 03_strings -->
```fusion
void function main()
    string name = "Ada"
    int age = 36
    print("{name} is {age}")                       // a name or a field path inside {}
    print("{@2}, {@1}!", "World", "Hello")          // any order, repeatable
    print("100% sure")                              // % is printed as-is
    string line = "{name} is {age}"                // a {...} string is a value anywhere
    string greeting = format("{@2}, {@1}!", "World", "Hello")   // format = print's text
    print(line + " / " + greeting)
    print("\{name\} is written as \{name\}")      // \{ \} - a brace as text: {name} is written as {name}
```

#### String templates: `template string greet = "Hello {@1}"`

<!-- example: syntax_templates | task: 29.3 | folder: 02_functions -->
```fusion
const string SHOP = "Ann's Cafe"
template string welcome = "Welcome to {SHOP}, {@1}!"     // works like a function

void function show((string) -> string line, string who)
    print(line(who))

void function main()
    string city = "Paris"
    template string greet = "Hello {@1}, you are {@2} - {city}"
    print(greet("Ann", 30))             // {@1} {@2} filled; {city} read when called
    city = "Rome"
    print(greet("Bob", 2))
    print(welcome("Cy"))
    show(welcome, "Di")                 // passed where a function type is written
```

#### Numbers as conditions: `if count` (`[conditions] numbers`)

<!-- example: syntax_number_conditions | task: 30.9 | folder: 01_basics -->
```fusion
void function main()
    int count = 3
    int errors = 0
    int found = -1                       // "not found"
    bool ready = true
    if count and ready                   // count > 0 - the default, "positive"
        print("go")
    if not errors
        print("no errors")
    if found                             // -1 is false with "positive" (true with "nonzero")
        print("found")
    else
        print("not found")
    int left = 3
    while left                           // while left > 0
        left = left - 1
    print("{left}")                      // bool b = count stays an error: write count > 0
```

#### The conditional operator: `(condition) ? a : b`

<!-- example: syntax_conditional | task: 30.7 | folder: 01_basics -->
```fusion
void function main()
    int count = 7
    string size = (count > 5) ? "big" : "small"      // one line, gives a value
    int band = (count > 100) ? 3 : (count > 5) ? 2 : 1
    print("{size} {band}")
    print((count % 2 == 0) ? "even" : "odd")          // only the chosen value runs
```

#### Long lines: a line break inside `( )` or `[ ]` continues the line

<!-- example: syntax_long_lines | task: 44.3 | folder: 01_basics -->
```fusion
int function total(int a, int b, int c) : a + b + c

void function main()
    int[] scores = [10,
                    20,
                    30]
    print("{@1} + {@2} + {@3} = {@4}",
          scores[0],
          scores[1],
          scores[2],
          total(scores[0],
                scores[1],
                scores[2]))
```

#### Generic functions: one function for many types

<!-- example: syntax_generics | task: 33.2a | folder: 09_generics -->
```fusion
T function first<T>(List<T> items) : items[0]               // the type parameters after the name
T function last(List<T> items) : items[items.len() - 1]     // also accepted: T, K, V (and T1, K2) in a signature
V function valueOf<K, V>(Map<K, V> m, K key) : m[key]       // Key and Value
T1 function second<T, T1>(List<T> a, List<T1> b) : b[0]    // several types - the result may be any of them

struct Pair<A, B>                                           // a generic struct (33.2b)
    A first
    B second
    A function left() : first                               // methods too (33.2c)

class Box<T>                                                // a generic class (33.2c)
    T item
    constructor(T item)
        this.item = item
    T function take() : item
    void function put(T x)
        item = x

class Named
    public string name

class Tag<T> inherits Named                                 // a parent and interfaces too (33.3a)
    T value
    constructor(string name, T value)
        this.name = name
        this.value = value

class Garage<T>                                             // no constructor: a List starts empty
    List<T> items
    void function park(T item)
        items.add(item)
    int function count() : items.len()

void function main()
    List<int> numbers = [3, 1, 2]
    List<string> names = ["Ada", "Bo"]
    print("{@1} {@2} {@3}", first(numbers), first(names), last(names))    // 3 Ada Bo - types from the arguments
    print("{@1}", first<int>(numbers))                                    // 3 - or written
    Map<string, int> ages
    ages["Ada"] = 36
    print("{@1} {@2}", valueOf(ages, "Ada"), second(numbers, names))      // 36 Ada
    Pair<int, string> p = Pair(1, "one")                                  // types from the values, or Pair<int, string>(...)
    print("{@1} {@2}", p.first, p.second)                                 // 1 one
    Box<string> b = Box("hat")                                            // T from the constructor's values
    b.put("cap")
    print("{@1} {@2}", b.take(), p.left())                                // cap 1
    Garage<string> g = Garage()                                           // T from the left - written once (33.5)
    g.park("van")
    print("{@1}", g.count())                                              // 1
    Named n = Tag("size", 42)                                             // a Tag<int> where a Named is expected
    print(n.name)                                                         // size
```
A generic function names its types in `<...>` after its name, or uses T, K, V (Type, Key, Value - and T1, K2 ...)
in its signature (D.166); a struct, class or enum can't be named T, K or V. At a call the types come from the
arguments, or are written - `first<int>(numbers)`; where they can't be worked out the error says to write them.
One C function is made for each set of types used (`first__int`, `first__string`) - no run-time cost. Without a
condition a T can be stored, passed, returned, compared with `==` and printed. A generic struct (`struct Pair<A, B>`)
is made once per set of types used too - `Pair<int, string>`; its types come from the values given, or are written;
it works as any struct (copies, `==`, a field of another struct, `List<Pair<int, string>>`). A generic class
(`class Box<T>`) and a generic struct's methods are copied with it - `Box<int>` gets its own `take`, `put` and
constructors; the types come from the constructor's values, or are written (`Box<string>("hat")`); inside its own
methods `Box(...)` and `Box<T>` mean this copy. A generic class may have a parent and interfaces that don't name T
(`class Tag<T> inherits Named implements Printable`) - each copy builds on them; one naming T (`inherits Box<T>`) -
the next section; statics come later (33.3c).
Stored where its type is written - a variable, a field, a parameter, a result - a generic class or struct takes its
types from there: `Garage<string> g = Garage()` (D.171); the arguments are then checked against them
(`Box<Car> b = Box("hat")` - expected Car, got string). With `var` / `let` there is no type on the left: write it.

#### A generic class on a generic parent or interface: `inherits Box<T>`, `implements Collection<T>`

<!-- example: syntax_generic_parents | task: 33.3b | folder: 09_generics -->
```fusion
class Box<T>
    public T item
    constructor(T item)
        this.item = item
    string function kind() : "box"

class Special<T> inherits Box<T>                       // Special<int> builds on Box<int>
    constructor(T item)
        super(item)
    override string function kind() : "special"

class IntBox inherits Box<int>                         // a plain class on a generic parent
    constructor(int n)
        super(n)

class BagIterator<T> implements Iterator<T>
    List<T> items
    int at = 0
    constructor(List<T> items)
        this.items = items
    bool function hasNext() : at < items.len()
    T function next()
        at = at + 1
        return items[at - 1]

class Bag<T> implements Collection<T>                  // a generic collection of your own
    List<T> items
    Iterator<T> function iterator() : BagIterator<T>(items)
    bool function add(T x)
        items.add(x)
        return true
    bool function remove(T x) : false
    int function length() : items.len()
    bool function isEmpty() : items.len() == 0
    bool function contains(T x) : false
    bool function addAll(Collection<T> xs) : false
    bool function removeAll(Collection<T> xs) : false
    bool function keepOnly(Collection<T> xs) : false
    void function clear()
        items.clear()

string function describe(Box<int> b) : format("{@1} {@2}", b.kind(), b.item)

void function main()
    Special<int> s = Special(5)                       // the types written once - on the left
    print(describe(s))                                // special 5 - a Special<int> is a Box<int>
    print(describe(IntBox(9)))                        // box 9
    Bag<string> names = Bag()
    names.add("Ada")
    names.add("Bo")
    foreach (string n in names)
        print(n)                                      // Ada / Bo
```
A generic class may build on a generic one - `inherits Box<T>` (`Special<int>` builds on `Box<int>`, and is one), or
`inherits Box<int>` from a plain class - and answer an interface with its types - `implements Collection<T>`, so a
generic collection of your own works in `foreach` and where a `Collection<int>` is expected. Such a class is copied
before inheritance is worked out, from the types written in the program: write its types where it is used, on the left
is enough (`Special<int> s = Special(5)`); a call alone (`print(Special(5).kind())`) says to write them (33.3b).

#### Statics on a generic class: one set per copy

<!-- example: syntax_generic_statics | task: 33.3c | folder: 09_generics -->
```fusion
class Box<T>
    public static int made = 0                        // one per copy: Box<int>.made, Box<string>.made
    public static T last                              // of the copy's type - an int in Box<int>
    T item
    constructor(T item)
        this.item = item
        made = made + 1                               // inside the class: this copy's own
        last = item
    public static int function count() : made

void function main()
    Box<int> a = Box(1)
    Box<int> b = Box(2)
    Box<string> c = Box("hat")
    print("{@1} {@2}", Box<int>.made, Box<string>.made)       // 2 1
    print("{@1} {@2}", Box<int>.last, Box<string>.last)       // 2 hat
    print("{@1}", Box<int>.count())                           // 2
```
Each copy of a generic class has its own statics (D.173) - written with the types outside the class
(`Box<int>.made`; `Box.made` alone says to write them), by name inside it. `[generics] sharedStatics = true` gives
one set for all copies instead, written `Box.made` - then a static of type T is an error, since one value can't be of
each copy's type.

#### Generic conditions: what a type parameter may be

<!-- example: syntax_generic_conditions | task: 33.2d | folder: 09_generics -->
```fusion
interface Printable
    string function label()

class Vehicle
    public string name
    constructor(string name)
        this.name = name

class Car inherits Vehicle implements Printable
    constructor(string name)
        super(name)
    string function label() : "car {name}"

T function total<T extends Number>(List<T> xs)             // any number type
    T sum = xs[0]                                           // the first item starts it (0 is an int, T may not be)
    for i in 1...xs.len() - 1                               // then the rest: 1 to the last index, both ends included
        sum = sum + xs[i]
    return sum

T function totalToo<T extends Number>(List<T> xs)          // the same with range(start, end) - end left out
    T sum = xs[0]
    for i in range(1, xs.len())                             // 1 to len - 1: range leaves its end out
        sum = sum + xs[i]
    return sum

int function count<T extends int>(List<T> xs) : xs.len()   // only int
string function park<T : Vehicle>(T v) : v.name            // Vehicle or a child of it (':' = extends)
string function show<T extends Vehicle implements Printable>(T v) : v.label()   // both

class Box<T implements Printable>                           // on classes and structs too
    T item
    constructor(T item)
        this.item = item
    string function shown() : item.label()

void function main()
    List<int> ns = [1, 2, 3]
    print("{@1} {@2} {@3}", total(ns), totalToo(ns), count(ns))   // 6 6 3
    print(park(Vehicle("van")))                             // van
    print(show(Car("mini")))                                // car mini
    Box<Car> b = Box(Car("cab"))
    print(b.shown())                                        // car cab
```
A condition sits where the type parameter is named (D.167): `T extends Vehicle` (or `T : Vehicle`) - Vehicle or a
child of it; `T extends Number` - any number type; `T extends int` - only int; `T implements Printable` - only a type
that implements it; several interfaces `<T implements Comparable, Printable>`; both, extends first
`<T extends Vehicle implements Comparable>`. A type that doesn't meet one is a compile error at the use, naming the
type and the condition - `park(Aircraft("x"))`: "'park' <T extends Vehicle>: Aircraft is not Vehicle or a child of it";
`Box<Aircraft>` the same. After `implements`, a name after a comma is one more interface unless it is one capital
letter (with digits) - `<T implements Comparable, K>` starts K. `where` stays reserved.
`[generics] enabled = false` turns them off (D.168).

#### Any number of values: `int... numbers`, `T... items`

<!-- example: syntax_variadic | task: 33.2e | folder: 02_functions -->
```fusion
int function sum(int... numbers)                    // the last parameter; a List<int> inside
    int total = 0
    for n in numbers
        total = total + n
    return total

string function joinAll(string sep, string... parts)
    string text = ""
    for p in parts
        if text != ""
            text = text + sep
        text = text + p
    return text

T function firstOf(T... items) : items[0]            // generic - T from the values

void function main()
    int[3] a = [4, 5, 6]
    List<int> xs = [7, 8]
    print("{@1} {@2} {@3} {@4}", sum(1, 2, 3), sum(), sum(a), sum(xs))   // 6 0 15 15
    print(joinAll(", ", "x", "y", "z"))              // x, y, z
    print(firstOf("p", "q"))                         // p
```
A parameter written `int... numbers` takes the values left over at the call: written one by one (none gives an
empty List), one array, or one List - inside the function it is a `List<int>`. It must be the last parameter and
has no default. The values are lent to the call (an object passed this way is still usable after it).
`T... items` works the same in a generic: T comes from the values (all of one type), or the List / array's element;
values of several types that all meet a condition (`<T extends Vehicle>(T... vs)` - a Car and a Bus) make T the
condition's type. `main`'s `string... args` stays an array.

<!-- example: syntax_variadic_pack | task: 33.2e2 | folder: 09_generics -->
```fusion
void function show(T... items)                      // no condition: values of any type each - a pack
    print("{@1} values", items.len())
    for x in items                                   // written out once per value, x of that value's type
        print("{@1}", x)

void function main()
    show(1, "two", 3.5)                              // 3 values / 1 / two / 3.500000
    show(true, 'c')                                  // 2 values / true / c
```
Values of different types with no condition on T make a pack (as C++'s variadic templates): the function is made
once for each combination of types used (`show<int, string, double>`), each value keeping its own type. Inside,
the pack can be looped (`for x in items` - the body written out per value, T that value's type there), counted
(`items.len()`, `len(items)`) or read by a written number (`items[1]`); passing it whole, a computed index, T
outside the loop, T as the result, and `break` / `continue` in that loop are errors that say why. With a condition
(`<T extends int>`) the values must all meet it instead.

#### Lambdas and function values

<!-- example: syntax_lambdas | task: 18.1.3 | folder: 02_functions -->
```fusion
int function apply((int) : int f, int v) : f(v)
int function triple(int x) : x * 3

void function main()
    (int) : int twice = func(int x) : x * 2
    print("{@1} {@2}", apply(twice, 5), apply(triple, 5))   // named functions are values too
```

#### Arrays

<!-- example: syntax_arrays | task: 18.2.4 | folder: 04_arrays -->
```fusion
int function sum(int[] values)          // any size, passed by reference
    int total = 0
    for i in range(0, len(values))
        total = total + values[i]
    return total

int[3] function podium() : [3, 1, 2]    // returned arrays need a size

void function main()
    int[] scores = [10, 20, 30]         // size from the literal
    float[3] buffer                     // zero-filled
    int[] none                          // empty - size 0
    int also[] = [4, 5]                 // the same as int[] also - brackets after the name
    fixed int[3] top = [3, 2, 1]        // fixed: never another size (top = [1, 2] is an error)
    scores[0] = 99
    int[3] p = podium()
    print("{@1} {@2} {@3} {@4} {@5} {@6}", sum(scores), len(scores), buffer[0], p[0], none.length, top[0])
    try
        scores[5] = 1                       // every index is checked: an IndexError
    catch IndexError e
        print("{e}")
```

#### The `Array` class: every array acts as an object

<!-- example: syntax_array_class | task: 45.1 | folder: 04_arrays -->
```fusion
struct Point
    int x
    int y

void function main()
    int[] scores = [10, 20, 30]
    print("{@1}", Array.length(scores))     // 3 - through the Array class
    print("{@1}", scores.length)            // 3 - the same, as a method of the array
    List<int> copy = Array.toList(scores)   // the same as scores.toList()
    copy.add(40)
    print("{@1} {@2}", copy.len(), scores.length)   // 4 3 - the array is unchanged
    Point[] pts = [Point(1, 2), Point(3, 4)]
    print(Array.toCSV(pts, ";"))            // the same as pts.toCSV(";")
```
Every array acts as if it were an object of the built-in `Array` class (D.142): `Array.length(a)`,
`a.length`, `a.length()`, `a.len()` and `len(a)` are one call. Its methods today: `length` (`len`),
`toList`, `toCSV`. `Array` is a built-in name - a struct, class or enum can't take it.

#### Copying a part: `copyPart` / `copyPartAt`

<!-- example: syntax_array_copy_part | task: 45.5 | folder: 04_arrays -->
```fusion
void function show(int[] xs)
    foreach (int x in xs)
        write("{x} ")
    print("|")

void function main()
    int[] some = [20, 30, 40]
    show(some.copyPart(1, 2))           // 30 40 |    - start, count
    show(some.copyPart(1, 9))           // 30 40 |    - a count past the end stops there
    show(some.copyPartAt(0, 1))         // 20 30 |    - start, end - the end included
    show(some.sliceAt(2, 0))            // 40 30 20 | - start after end: reversed
    try
        show(some.slice(3, 1))          // a start outside: an IndexError
    catch IndexError e
        print("{e}")
    List<string> names = ["a", "b", "c"]
    List<string> last = names.copyPart(1, 2)      // Lists the same: a new List
    print("{@1}", last.len())           // 2
```
Both copy and leave the original unchanged (D.046); `slice` / `sliceAt` are quick typing for them.
Positions count from 0. An array gives a new array (on the heap - `int:[] g = a.copyPart(0, 2)` makes it
growable), a List a new List; a string is copied, an object shared.

#### Arrays of 2 and 3 dimensions

<!-- example: syntax_many_dims | task: 45.12a | folder: 04_arrays -->
```fusion
void function main()
    int[2][3][4] cube                   // 2 rows x 3 columns x 4 depth - also int[2],[3],[4] cube
    cube[1][2][3] = 5                   // row 1, column 2, sheet 3 (from 0)
    cube[0],[1],[2] = 7                 // the same as cube[0][1][2]
    print("{@1} {@2}", cube[1][2][3], cube[0][1][2])            // 5 7
    print("{@1} {@2} {@3}", cube.rows, cube.columns, cube.depth)  // 2 3 4
    print("{@1}", cube.length)          // 4 - the outer dimension first: depth
    int[][] m = [[1, 2, 3], [4, 5, 6]]  // the sizes from the values: 2 rows x 3 columns
    m[1][2] = 60
    print("{@1} {@2} {@3}", m[0][2], m[1][2], m.length)         // 3 60 3
    try
        int r = 5
        print("{@1}", m[r][0])          // each index is checked against its own size
    catch IndexError e
        print("{e}")
```
Up to 3 dimensions in the core - rows x columns x depth (D.143); every row the same length. `length`
gives the outer dimension first - depth, then columns, then rows (`[arrays] order`, D.148); `rows` and
`columns` on 2 and 3 dimensions, `depth` on 3. The array is one block on the stack, laid out in that
order. Views (`cube[1]`, `cube[][2]`), loops over it, passing and copying it come with Task 45.12b-c.

#### Parts of an array - views, and foreach over many dimensions

<!-- example: syntax_many_dims_views | task: 45.12b | folder: 04_arrays -->
```fusion
void function main()
    int[][] m = [[1, 2, 3], [4, 5, 6]]  // 2 rows x 3 columns
    foreach (int[] column in m)         // the outer dimension first: its 3 columns
        foreach (int v in column)       // each column's 2 values, one per row
            write("{v} ")               // 1 4 2 5 3 6
    print("")
    foreach (int v in m[1])             // row 1 - an index left out means all of it
        write("{v} ")                   // 4 5 6
    print("")
    foreach (int v in m[][2])           // column 2 - one value per row
        write("{v} ")                   // 3 6
    print("")
    int[] row = m[0]                    // a copy - numbers and strings copied, objects shared
    row[0] = 9
    print("{@1} {@2} {@3}", row[0], m[0][0], m[1].length)    // 9 1 3
    print("{@1}", m[1][2].length)       // -1 - one slot has no length
```
A part of an array is a **view** (D.149): `cube[1]` (row 1), `cube[][2][1]` (column 2 of sheet 1),
`cube[][][3]` (sheet 3). In a `foreach` it is borrowed - nothing is copied, and writing to it writes
the array; given to a variable it is a copy (`byVal` copies its objects too). `foreach` and `length`
take the outer dimension first: depth, then columns, then rows (`[arrays] order = "rows"`: rows first).

#### toList on arrays of 2 and 3 dimensions

<!-- example: syntax_many_dims_to_list | task: 45.11 | folder: 04_arrays -->
```fusion
void function main()
    int[][] m = [[1, 2, 3], [4, 5, 6]]  // 2 rows x 3 columns
    List<List<int>> columns = m.toList()            // the outer dimension first, as foreach
    print("{@1} {@2}", columns.len(), columns[2][1])        // 3 6 - its 3 columns, 2 values each
    List<int> row = m[1].toList()       // a part: row 1
    print("{@1}", row.len())            // 3
```
`toList()` gives a List of Lists in the loop's order - depth, then columns, then rows (`[arrays] order =
"rows"`: rows first). It is a copy. A List never holds null (D.139): an object or enum slot that is
null is skipped - a column whose slots are all null is an empty List (D.152).

#### A whole array given to a new one

<!-- example: syntax_array_whole_copy | task: 45.12e | folder: 04_arrays -->
```fusion
void function main()
    int[2][3] m = [[1, 2, 3], [4, 5, 6]]
    int[][] copy = byVal m              // a copy - m stays usable
    copy[0][0] = 9
    print("{@1} {@2}", m[0][0], copy[0][0])     // 1 9
    int[2][3] n = m                     // m moves to n - m can't be used after
    print("{@1}", n[1][2])              // 6
    string[3] a = ["x", "y", "z"]
    string[] b = a                      // one dimension the same
    print("{@1}", b[2])                 // z
    n = [[7, 8, 9], [1, 2, 3]]          // replaced - the same shape
    print("{@1}", n[0][0])              // 7
    int[2][2] g = [[1, 2], [3, 4]]
    g = [[5, 6, 7]]                     // another shape - g lives on the heap
    print("{@1} {@2}", g.rows, g.columns)       // 1 3
```
A whole array given to a new one moves, as a List does (D.025): its slots are copied and the old name
can't be used after - use `byVal` for a copy that leaves it usable (objects copied too). The sizes are
taken from the source when left out (`int[][] n = m`); written, they must agree. A whole array of 2 or
3 dimensions is replaced by values, another array or a function's result of the same shape
(`n = [[...]]`, `n = m`, `n = make()`). Given values of another shape, a plain array lives on the heap
(as one-dimension arrays do, 45.10) - it still never grows by itself (`expand` is for `int:[][]`); a
growable array takes any shape. A fixed array is never replaced.

#### toCSV on arrays of plain values

<!-- example: syntax_array_csv | task: 45.11b | folder: 04_arrays -->
```fusion
void function main()
    int[] a = [1, 2, 3]
    print(a.toCSV())                    // 1,2,3 - one line
    int[][] m = [[1, 2, 3], [4, 5, 6]]
    print(m.toCSV())                    // a line per row: 1,2,3 then 4,5,6
    print(m.toCSV(";", "#", " | "))     // 1;2;3 | 4;5;6
    print(m.toCSV(lineDelimiter = "/")) // 1,2,3/4,5,6
    int[2][2][2] c                      // rows x columns x sheets
    c[0][0][1] = 5
    print(c.toCSV())                    // 0,0#5,0 then 0,0#0,0 - the sheets side by side
    string[] s = ["a", "b,c", "say \"hi\""]
    print(s.toCSV())                    // a,"b,c","say ""hi""" - the CSV rules
```
`toCSV(primaryDelimiter = ",", secondaryDelimiter = "#", lineDelimiter = "\n")` works on any array of
numbers, strings, bools, chars or enums - one dimension, two, three, a part (`m[1].toCSV()`) or a
growable one (D.151). A line per row, the values split by the primary delimiter; on 3 dimensions each
line holds that row of every sheet, the sheets split by the secondary delimiter
(`[arrays] csvManyDimensions = false` makes that a compile error). A value holding a delimiter, a quote
or a line break is wrapped in quotes, a quote inside doubled; a null slot is an empty field (`1,,3`).
A float is written as short as it can be (`1.5`, `2`). Arrays of structs keep the heading-row form below.

#### Growable arrays of 2 and 3 dimensions: `expand`

<!-- example: syntax_many_dims_growable | task: 45.12d | folder: 04_arrays -->
```fusion
void function main()
    int:[][] g = [                      // growable - also int:[2][3] g or int[[2],[3]] g
        [1, 2, 3],
        [4, 5, 6]]
    g.expand(ROWS, 1)                   // a warning: every slot is copied - now 3 x 3
    print("{@1} {@2} {@3}", g.rows, g[2][0], g[1][2])          // 3 0 6
    g.expand(COLUMNS, 2)                // 3 x 5 - two new columns at the right of every row
    g[2][4] = 9
    print("{@1} {@2}", g.columns, g[2][4])                      // 5 9
    int[[2],[2],[2]] cube
    cube[1][1][1] = 7
    cube.expand(DEPTH, 1)               // a new sheet at the back - it stays a cube
    print("{@1} {@2}", cube.depth, cube[1][1][1])               // 3 7
```
Only a growable array expands (D.141, D.143) - `int:[2][3]`, `int[[2],[3]]` or `int:[][] g = [...]` (best over
several lines). `expand(ROWS / COLUMNS / DEPTH, n)` - the built-in enum `Dimension` - adds n at the end of that
dimension; new slots get the default value (0, "", null). It lives on the heap; slots, parts, `foreach` and
passing it to an `int[][]` parameter work as on any array. Not inside a loop over it; `expand(0, 1)` and a
fourth dimension come with the Collections library.

#### Jagged arrays: each row its own length (`setStorage(JAGG)`)

<!-- example: syntax_jagged | task: 45.15 | folder: 04_arrays -->
```fusion
void function main()
    int:[][] j = [[1], [2, 3, 4], [5, 6]]
    j.setStorage(JAGG)                  // right after the declaration (or in its set-up block)
    print("{@1} {@2} {@3}", j.rows, j.columns, j[1].columns)   // 3 0 3 - no row given: 0 columns
    j[0].add(9)                         // one row grows on its own
    j.add([7, 8])                       // a new row
    foreach (int[] column in j)         // columns first (the default order): rows too short skipped
        print("{@1} slots, first {@2}", column.length, column[0])
    int:[][] empty
    empty.setStorage(JAGG)
    print("{@1} {@2}", empty.rows, empty.columns)              // 0 0 - an array is empty by default
```
A jagged array is a growable array of 2 dimensions whose rows each have their own length (D.144, D.153). It
says so right after it is made - `j.setStorage(JAGG)`, the next line or in its set-up block (D.147); on a plain
array that is an error. `j.rows` is how many rows, `j[r].columns` one row's length, and `j.columns` - no row
given - is 0 (D.163); `j.length` is an error that says which to use. Only `j[x][y]` outside a row is an
IndexError. `foreach` follows `[arrays] order`: columns first by default (each column a new array from the rows
long enough for it), `order = "rows"` gives each row as it is. A row passes to an `int[]` parameter. Passing
the whole, copying, `toList`, `toCSV`, `==`, `j[][1]` and 3 dimensions come later; `setStorage(FLAT)` /
`null` is the default (one block), `RECT` comes later (D.164).

#### Functions with arrays of 2 and 3 dimensions

<!-- example: syntax_many_dims_functions | task: 45.12c | folder: 04_arrays -->
```fusion
int function total(int[] values)
    int t = 0
    foreach (int v in values)
        t = t + v
    return t

int function sumAll(int[][] m)          // any size - its sizes come with it
    int t = 0
    foreach (int[] column in m)
        foreach (int v in column)
            t = t + v
    return t

void function setCorner(int[2][3] m)    // exactly 2 x 3 - the caller's array itself
    m[0][0] = 99

int[2][2] function identity()           // returns one of that shape
    int[][] i = [[1, 0], [0, 1]]
    return i

void function main()
    int[][] m = [[1, 2, 3], [4, 5, 6]]
    print("{@1} {@2} {@3}", sumAll(m), total(m[1]), total(m[][2]))   // 21 15 9
    setCorner(m)
    print("{@1}", m[0][0])              // 99
    int[2][2] id = identity()
    int[][] same = [[1, 0], [0, 1]]
    print("{@1}", id == same)           // true - slot by slot, the same shape
```
A parameter `int[2][3] m` takes that shape - the caller's array, by reference; `int[][] m` takes any
size. A part (`m[1]`, `m[][2]`) passed to a parameter is a copy (D.149) - of numbers for now; for
strings or objects copy it into a variable first. `==` needs the same shape (2 x 3 is not 3 x 2).

#### Combining arrays: `a + b + c`

<!-- example: syntax_array_combine | task: 45.4 | folder: 04_arrays -->
```fusion
void function main()
    int[] a = [1, 2]
    int[3] b = [3, 4, 5]
    int[] all = a + b + [6]             // a new array: [1, 2, 3, 4, 5, 6]
    print("{@1} {@2}", all.length, all[5])      // 6 6
    string[] s = ["x", "y"]
    string[] twice = s + s              // the strings are copied
    print("{@1}", twice.length)         // 4
    int:[] grows = a + [7]              // a growable one from it
    grows.add(8)
    print("{@1}", grows.length)         // 4
    List<int> la = [1, 2]
    List<int> lb = la + [3]             // Lists the same: a new List
    print("{@1}", lb.len())             // 3
```
`+` makes a new array from the parts, left to right, all of one type (D.047); the parts are unchanged.
Its size is only known while running, so it lives on the heap (45.10). Items are copied as `slice`
copies them: a string copied, an object shared. An array and a List don't mix - `toList()` first.

#### Replacing an array with another size

<!-- example: syntax_array_resize | task: 45.10 | folder: 04_arrays -->
```fusion
int function total(int[] values)        // any size
    int t = 0
    foreach (int v in values)
        t = t + v
    return t

int[] function firstN(int n)            // int[] - an array of any size
    if n > 2
        return [1, 2, 3]
    return [1]

void function main()
    int[] a = [5, 2, 3]
    a = [7, 8]                          // replaced - another size is fine
    print("{@1} {@2}", a.length, total(a))      // 2 15
    a = firstN(5)
    print("{@1} {@2}", a.length, total(firstN(1)))   // 3 1
    fixed int[2] pair = [1, 2]
    // pair = [1, 2, 3] here: 'pair' is fixed - its size never changes
```
A plain array gets a new size only by being replaced (D.141). Such an array lives on the heap - a
counted block, like a List - and still acts as an array: it is passed to an `int[]` parameter, every
index is checked, and it doesn't grow with `add` (that is `int:[]`, Task 45.3). An array of objects may
hold null in a slot (D.140). `fixed` keeps the size it was made with.

#### A growable array: `int:[]` or `int[[]]`

<!-- example: syntax_growable_array | task: 45.3 | folder: 04_arrays -->
```fusion
class Car
    public string color
    constructor(string c)
        this.color = c

void function main()
    int:[] readings                 // empty, can grow - also written int[[]] readings
    readings.add(4)
    readings.add(6)
    readings.add(9)
    int last = readings.removeLast()     // 9 - given back; [4, 6] left - pop() is the same
    print("{@1} {@2} {@3}", last, readings.length, readings[1])     // 9 2 6
    int:[3] slots                   // 3 slots made ahead: [0, 0, 0] - also int[[3]] slots
    slots.add(5)                    // [0, 0, 0, 5]
    print("{@1}", slots.length)     // 4
    Car:[] cars
    cars.add(Car("red"))
    cars.add(null)                  // an array of objects may hold null (D.140)
    foreach (Car c in cars)
        if c is not null
            print(c.color)          // red
        // cars.add(...) or cars.pop() here: a compile error - it is being looped over (D.058)
    try
        int:[] none
        none.removeLast()           // nothing to remove: an IndexError
    catch IndexError e
        print("{e}")
```
A growable array grows and shrinks only at its end (D.141): `add`, `removeLast` (`pop`), which gives
the removed item back - the caller owns it (a string or object lives on). Nothing is
inserted in the middle, so an item never moves - a List does that. It lives on the heap; it is passed
to an `int[]` parameter like any array. `fixed` can't go with it.

#### An array as a `Collection<T>`

<!-- example: syntax_array_collection | task: 45.10 | folder: 04_arrays -->
```fusion
int function total(Collection<int> c)
    int sum = 0
    foreach n in c
        sum = sum + n
    return sum

void function main()
    int[3] a = [1, 2, 3]
    print("{@1}", total(a))                           // 6 - an array where a Collection<int> is expected
    Collection<int> c = a                             // a copy of its values
    print("{@1} {@2}", c.length(), c.contains(2))     // 3 true
    try
        c.remove(1)                                   // an array keeps its items (D.090)
    catch ReadOnlyError e
        print(e.message)
    int:[] g = [5, 6]
    Collection<int> grows = byRef g                   // a growable array: the array itself
    grows.add(7)                                      // adding grows it
    print("{@1}", g.len())                            // 3
```
An array is a `Collection<T>` (D.090) with an implementation of its own: reading works - `iterator()`, `length()`,
`isEmpty()`, `contains()`, `foreach` - and removing is a ReadOnlyError (`remove`, `removeAll`, `keepOnly`, `clear`). A
growable array (`int:[]`) is given as itself, so `add` grows it; a plain or fixed one (`int[3]`) is given as a copy of its
values - a stack array can't outlive its function - so `add` is refused too (an array keeps its size). Strings in the
copy are copied, objects shared. An array of 2 or 3 dimensions: give its `toList()`.

#### Structs (fields only, copied by value)

<!-- example: syntax_structs | task: 18.2 | folder: 07_structs -->
```fusion
struct Point
    int x
    int y

struct Player {
    string name
    float health = 100.0
    int[3] scores
}

struct Line
    Point a
    Point b
End struct

Point function add(Point p, Point q) : Point(p.x + q.x, p.y + q.y)

void function main()
    Point a = Point(3, 4)
    Point b = a                         // a copy
    b.x = 10
    Point n = Point(y = 2, x = 1)       // named construction
    Player ada = Player("Ada", scores = [5, 6, 7])
    Line l = Line(a, n)
    l.b.y = 9
    Point[] pts = [Point(1, 1), add(a, n)]
    print("{@1} {@2} {@3} {@4} {@5}", a.x, b.x, ada.health, l.b.y, pts[1].x)
```

#### Enums

<!-- example: syntax_enums | task: 25.2 | folder: 06_match_and_enums -->
```fusion
enum Color: Red Green Blue                // one line - commas are optional

enum Status                               // a block (braces and End enum work too)
    OK = 200                              // values count up from 0 unless given
    NotFound = 404

struct Pixel
    int x
    Color color = Color.Blue              // an enum field, with a default

void function main()
    Color c = Color.Green
    Status s                              // no value given: its first one, OK
    print("{c} {s} {@1} {@2}", c.toInt(), Status.NotFound.toInt())
    if c == Color.Green and c != Color.Red    // only values of the same enum compare
        print("green, " + c.toString())
    for each in Color.values()            // every value, in order
        print("{each}")
    Map<Color, int> votes                 // an enum as a Map key, a List element, ...
    votes[Color.fromString("Red")] = 3    // text to value - an unknown name stops the program
    print("{@1} {@2}", votes[Color.Red], Pixel(1).color)
```

#### An enum value alone where the type is known

<!-- example: syntax_enum_bare | task: 45.17 | folder: 06_match_and_enums -->
```fusion
enum Months: JANUARY FEBRUARY MARCH JUNE

void function show(Months m)
    print("{m}")

Months function pick(bool late)
    if late
        return JUNE                     // a return of a Months
    return Months.MARCH                 // the full name always works

void function main()
    show(JUNE)                          // a parameter - the same as show(Months.JUNE)
    Months m = FEBRUARY                 // a declaration
    m = JANUARY                         // an assignment
    print("{@1} {@2}", m == JANUARY, JUNE == pick(true))     // comparisons: true true
    match m
        case JANUARY: print("january")  // a case - as before
        else: print("other")
```
Where a Months is expected, its value's name alone is enough (D.150). Anywhere else - `print(JUNE)`,
`int x = JUNE` - write `Months.JUNE`. A variable with the same name there is a compile error: write
`Months.JUNE`, or rename the variable.

#### Enums can be null: an unset enum is `null`

<!-- example: syntax_null_enums | task: 30.11 | folder: 10_errors_and_null -->
```fusion
enum Status
    OK
    NotFound

void function main()
    Status s                                   // no value given: null, not OK
    print("{s} {@1} {@2}", s == null, s?.null)  // also: s is null, s === null
    s = Status.NotFound
    if s is not null                           // also: s != null, !s?.null
        print("set: {s}")
    s = null
    match s
        case null: print("not set")            // at most one; without it, null goes to else
        case OK: print("ok")
        else: print("something else")
    try
        int n = s.toInt()                      // null has no number
    catch NullError e
        print("{e}")
```

#### Enums with data

<!-- example: syntax_enum_data | task: 25.4 | folder: 06_match_and_enums -->
```fusion
enum Shape                                // a value may carry data
    Circle(double radius)
    Rect(double width, double height)
    Empty

bool function isWide(Shape s)
    match s
        case Rect(w, _): return w > 2.0   // _ skips a value you don't need
        else: return false

double function area(Shape s)
    match s                               // the data is read only through match
        case Circle(r): return 3.14159 * r * r
        case Rect(w, h): return w * h
        case Empty: return 0.0

void function main()
    List<Shape> shapes = [Shape.Circle(1.0), Shape.Rect(height = 3.0, width = 2.0), Shape.Empty]
    for s in shapes
        print("{s}: {@1}", formatNumber(area(s), "0.00"))   // prints the value's name
    print("{@1} {@2}", Shape.Rect(2.0, 3.0) == shapes[1], isWide(shapes[1]))   // compares the value and its data
```

#### `match`

<!-- example: syntax_match | task: 25.3 | folder: 06_match_and_enums -->
```fusion
enum Light: Red Yellow Green

string function action(Light l)
    match l                               // every value needs a case (or an else)
        case Red, Yellow                  // several values share a case
            return "stop"
        case Green: return "go"           // one statement after ':'

void function main()
    for l in Light.values()
        print("{l}: {@1}", action(l))
    for ch in ['+', 'x', '7']
        match ch {                        // braces work too, and End match
            case '+', '-' {
                print("operator")
            }
            case '7': continue            // continue acts on the loop; break ends the match
            else: print("other")          // on an int, char or string: else is required
        }
```

#### `fall match`: falls through until `break`

<!-- example: syntax_fall_match | task: 30.13 | folder: 06_match_and_enums -->
```fusion
enum Level
    Low
    Mid
    High

void function main()
    Level level = Level.Mid
    fall match level                     // like a switch: the next cases run too
        case High: print("check the roof")
        case Mid: print("check the windows")
        case Low
            print("check the door")
            break                        // stop falling
    match level                          // a plain match never falls through
        case High: print("high")
        else: print("not high")
```

#### `let` and `var`: the type comes from the value

<!-- example: syntax_let_var | task: 46.1 | folder: 01_basics -->
```fusion
struct Point
    int x
    int y

int function grow(let int start, var int step)   // let: can't change in here; var: can
    step = step * 2
    return start + step

void function main()
    let name = "Ann"                    // string - set once, never changes
    var count = 0                       // int - can change, stays an int
    count = count + 2
    let home = Point(1, 2)              // nothing inside a let can change: home.x = 5 is an error
    let size                            // no value yet: set exactly once, on every path
    if count > 1
        size = "big"
    else
        size = "small"
    print("{name} {count} {home.x} {size} {@1}", grow(1, 3))   // Ann 2 1 big 7
```

#### `match` that gives a value

<!-- example: syntax_match_value | task: 46.2 | folder: 06_match_and_enums -->
```fusion
enum Light: Red Yellow Green

void function main()
    int n = 7
    string day = match n { 6, 7 : "Weekend", _ : "Weekday" }
    let size = match n
        0 : "none"
        1, 2, 3 : "few"
        _ : "many"
    Light l = Light.Green
    let action = match l { Red, Yellow : "stop", Green : "go" }   // every value: no _ needed
    print("{day} {size} {action}")      // Weekend many go
```
One value per case - no code, though a function call may fetch it; every possible value
covered; it never falls through. `_` and `else` both mean "anything else" (`_` preferred
here, `else` in a match statement, which takes `_` too).

#### `write`: print without ending the line

<!-- example: syntax_write | task: 46.3 | folder: 12_files_and_programs -->
```fusion
void function main()
    write("1 + 2 = ")                   // the line stays open
    write("{@1}", 1 + 2)
    print("")                           // ends it
```
`print` and `write` are for the console only - files have `writeText`, `appendText`.

#### Strings (values, freed automatically)

<!-- example: syntax_strings | task: 18.3.1 | folder: 03_strings -->
```fusion
string function shout(string word)
    word = "LOUD"                       // works on its own copy
    return word

void function main()
    string a = "apple"
    string b = a                        // an independent copy
    b = "banana"
    string loud = shout(a)
    print("{@1} {@2} {@3}", a, b, loud)
    print("{@1} {@2}", a == "apple", a < b)   // compares text; < > alphabetical
```

#### Changing a character: `s[i] = c`

<!-- example: syntax_string_put | task: 29.1 | folder: 03_strings -->
```fusion
void function main()
    string a = "Andrew"
    string b = a                        // an independent copy
    b[0] = 'X'                          // changes b's own text only
    string word = "cafe"
    word[3] = '\u00e9'                  // a wider character: the rest moves along
    print("{a} {b} {word}")
    const string name = "Ann"           // a const string never changes: name[0] = 'X' is an error
    try
        b[10] = 'z'                     // every index is checked: an IndexError
    catch IndexError e
        print("{e}")
```

#### String operations (each returns a new string)

<!-- example: syntax_string_operations | task: 18.3.2 | folder: 03_strings -->
```fusion
void function main()
    string name = "Ada"
    string full = name + " " + "Lovelace" + '!'   // join strings (and chars) with +
    print("{full}: {@1} characters, first {@2}", len(full), full[0])   // s[i] is bounds-checked
    print("[{@1}] [{@2}] [{@3}]", substring(full, 4, 8), toUpper(name), trim("  x  "))
    print("{@1} {@2} {@3} {@4}", contains(full, "Love"), indexOf(full, "Love"), startsWith(full, "Ada"), endsWith(full, "!"))

    string input = "42"
    if isInt(input)                                // check before converting
        int n = toInt(input)
        string text = toString(n * 2) + " / " + toString(2.5) + " / " + toString(true)
        print(text)
    // toInt("12x") would stop the program: Runtime error at file:line: '12x' is not a whole number
```

#### Unicode text (characters vs bytes)

<!-- example: syntax_unicode | task: 18.3.2b | folder: 03_strings -->
```fusion
void function main()
    string word = "caf\u00e9"          // the same as writing the accented letter directly
    string jp = "\u65e5\u672c"           // two Japanese characters
    print("{word}: {@1} characters, {@2} bytes", len(word), lenb(word))
    print("{jp}: {@1} characters, {@2} bytes", len(jp), lenb(jp))
    char e = word[3]                    // indexing counts characters
    print("{e} has code {@1}; {@2}", charCode(e), fromCharCode(65))
    print("{@1} [{@2}]", isAscii(word), asciiOnly(word, '?'))
    string joined = jp + '!' + e        // a char can be any character
    print(joined)
```

#### String library: inspect, search, extract, change, pad, number bases, formatting, compare, mask

<!-- example: syntax_string_library | task: 18.3.6 | folder: 03_strings -->
```fusion
void function main()
    string s = "caf\u00e9 au lait"
    print("{@1} {@2} {@3}", isEmpty(s), isBlank("  "), isDigits("2026"))
    print("{@1} {@2}", isLetters("Caf\u00e9"), countOf(s, "a"))         // letters: ASCII + Latin-1
    print("{@1} {@2} {@3}", indexOf(s, "a"), indexOf(s, "a", 2), lastIndexOf(s, "a"))
    print("{@1}", containsAny(s, "xyz!"))
    print("[{@1}] [{@2}] [{@3}]", left(s, 4), right(s, 4), left(s, 99))   // up to n: clamps
    print(replace("a-b-c", "-", " + "))                 // every match; replaceFirst for one
    print("{@1} {@2}", insert("Ada", 3, "!"), remove("Ada Lovelace", 3, 9))
    print("{@1} {@2}", repeat("ab", 3), reverse(s))
    print("[{@1}] [{@2}]", trimStart("  x  "), trimEnd("  x  "))
    print("{@1} / {@2} / {@3}", toUpper(s), capitalize("hello world"), toTitle("hello world"))
    print("[{@1}] [{@2}] [{@3}]", padLeft("7", 3, '0'), padRight("ab", 5), center("ab", 6, '*'))
    print("[{@1}]", truncate("Hello world", 8))       // the first 8 characters, nothing added

    int flags = 0xFF                                   // also 0b1010, 0o17, 1_000_000
    print("{@1} {@2} {@3}", toHex(flags), toHex("255", 4), toBinary(5, 8))
    print("{@1} {@2} {@3}", toHex(-1), fromHex("ffffffff"), fromHex("0x1F"))   // two's complement
    print("{@1} {@2} {@3}", toOctal(8), toBase(-255, 16), parseInt("z", 36))
    print("{@1} {@2}", bytesToHex("Hi"), hexToBytes("4869"))

    // formatNumber: Excel/.NET style, or printf style when the pattern starts with %
    print("{@1} {@2} {@3}", formatNumber(1234.5, "$#,##0.00"), formatNumber(7, "000"), formatNumber(0.256, "0.0%"))
    print("{@1} {@2} {@3}", formatNumber(3.14159, "%.2f"), formatNumber(42, "%05d"), formatNumber(3.5, "%.1f kg"))

    print("{@1} {@2}", equalsIgnoreCase("Hello", "hELLO"), compareIgnoreCase("apple", "BANANA"))
    print("{@1} {@2}", compareNatural("file2", "file10"), "file2" < "file10")   // -1 false

    print(formatMask("5551234567", "(###) ###-####"))   // # digit, A letter, ? any
    print("{@1} {@2}", mask("4111111111111111", 6, 4), maskEmail("alice@example.com"))
```

#### Files

<!-- example: syntax_files | task: 18.5.5 | folder: 12_files_and_programs -->
```fusion
void function main()
    string path = "fusion_example.txt"             // relative to the folder the program runs in
    writeText(path, "first line\n")               // creates or replaces the file
    appendText(path, "second line\n")
    print("{@1} line(s)", readLines(path).len())
    print(readText(path).trim())

    bytes raw = [0x00, 0xFF, 0x41]
    writeBytes("fusion_example.bin", raw)          // any bytes - for binary files
    print("{@1}", readBytes("fusion_example.bin").rawToHex())

    if fileExists(path)                            // a missing file is a run-time error,
        deleteFile(path)                           // so check first
    deleteFile("fusion_example.bin")
    print("{@1}", fileExists(path))
```

#### Program arguments, console input, exit

<!-- example: syntax_program_io | task: 18.5.4 | folder: 12_files_and_programs -->
```fusion
void function main(string... args)                // or main() with no parameters
    print("{@1} argument(s)", len(args))          // the program's name and --headless aren't in it
    for a in args
        print("[{a}]")
    print("Type lines, then end the input (Ctrl+Z, Enter on Windows):")
    int count = 0
    while not isEndOfInput()
        string line = readLine()                  // without its line ending
        count = count + 1
    print("{count} line(s)")
    if len(args) > 0 and args[0] == "stop"
        exit(2)                                   // end now, with an exit code
```

#### Running another program: `run`

<!-- example: syntax_run | task: 28.1.1 | folder: 12_files_and_programs -->
```fusion
void function main()
    print("before")
    int code = run("echo Hello from the shell")    // waits; its output appears here
    print("echo gave {code}")
    print("{@1}", run("exit 3"))                  // the program's exit code comes back
    if run("nosuchprogram_xyz") != 0              // a failing command is not an error
        print("that command failed")
    // run("notepad") opens Notepad and waits until it is closed (run("start notepad") doesn't wait)
    // run("python main.py hello.fusion") compiles a Fusion program; run("hello.exe") runs it
```

#### Lists: `List<T>`

<!-- example: syntax_lists | task: 18.5.1 | folder: 05_collections -->
```fusion
struct Team
    string name
    List<string> members

void function main()
    List<int> numbers = [3, 1, 2]                 // or List<int>() for an empty one
    numbers.add(10)
    numbers.insert(0, 7)
    numbers[1] = 5                                // bounds-checked
    numbers.sort()
    for n in numbers                              // each element in turn
        print("{n}")
    print("{@1} {@2} {@3}", numbers.len(), numbers.contains(5), numbers.indexOf(10))

    List<int> big = numbers.filter((int x) : x > 2)
    int total = numbers.reduce(0, (int sum, int x) : sum + x)
    print("{@1} {@2}", big.len(), total)

    List<string> names = ["Ada", "Grace"]
    List<string> copy = byVal names               // a copy - `copy = names` would move it
    copy.add("Linus")
    Team t = Team("core", byVal names)            // a copy - names alone would move into it
    t.members.add("Ken")
    print("{@1} {@2} {@3}", names.len(), copy.len(), t.members[2])

    List<List<int>> grid = [[1, 2], [3, 4]]
    grid[1][0] = 9
    print("{@1}", grid == [[1, 2], [9, 4]])

    List<string> parts = "a,b,,c".split(",")      // every piece, empty ones too
    print("{@1} {@2}", parts.len(), parts.join(" + "))   // also join(parts, " + ")
    print("{@1} {@2}", lines("one\ntwo\n").len(), words("  the quick  fox ").join("|"))
```

#### Shared or copied: `byVal` and `byRef`

<!-- example: syntax_shared_lists | task: 32.10a | folder: 05_collections -->
```fusion
struct Order
    List<string> items                  // copied when the Order is copied
    byRef List<string> log              // shared by the copies

void function addTo(List<int> xs)       // shared - the caller's list changes
    xs.add(9)

void function tryOut(byVal List<int> xs) // a copy - the caller's list stays as it was
    xs.add(100)

void function main()
    List<int> a = [1]
    List<int> b = byRef a               // the same list, borrowed (b = a would move it)
    b.add(2)
    print("{@1}", b.len())              // 2 - the borrow's last use
    List<int> c = byVal a               // a copy
    c.add(3)
    c.add(4)
    addTo(a)
    tryOut(a)
    print("{@1} {@2}", a.len(), c.len())   // 3 4

    Order first = Order(["tea"], ["opened"])
    Order second = byVal first          // a copy - its items too, not its log
    second.items.add("cake")
    second.log.add("copied")
    print("{@1} {@2} {@3}", first.items.len(), second.items.len(), first.log.len())   // 1 2 2
```
Rule of thumb: assigning a List / Map moves it (`[memory] ownership = "strict"`); `byVal`
copies it and `byRef` borrows it; passing it to a function lends it for the call. In a struct
copied with `byVal`, a `byRef` field stays shared (with `"share"`, assigning shares a List and
copies a struct). Never null - just empty
(`xs = null` is an error). Maps work the same way. Arrays follow once they can grow (Task 45).

`xs.toList()` gives a copy of a List (`xs.toList(false)`: the same list, shared), and
`scores.toList()` a new List from a one-dimensional array.

#### List options: `noDuplicates()`, `noNull()`, `readOnly()` in the set-up block

<!-- example: syntax_list_options | task: 32.14 | folder: 05_collections -->
```fusion
void function main()
    List<string> tags = ["a"] {
        tags.noDuplicates()               // a value it has can't be added again
        tags.add("b")
        tags.readOnly()                   // after this block, no more changes
    }
    print("{@1}", tags.len())             // 2
    // tags.add("c") here would be a compile error: read only after its set-up
```

#### Maps: `Map<K, V>` (also written `Dictionary<K, V>`)

<!-- example: syntax_map_entries | task: 32.6 | folder: 05_collections -->
```fusion
void function main()
    Map<string, int> ages
    ages["ann"] = 30
    ages["bob"] = 40
    foreach (Entry<string, int> e in ages)    // each key and value
        print("{e.key} {@1}", e.value)
    foreach name in ages.keys()              // borrowed - a view of the Map, no copy
        write("{name} ")
    print("")
    List<string> names = ages.keys().toList()   // a copy
    print(names[0])
```

<!-- example: syntax_maps | task: 18.5.2 | folder: 05_collections -->
```fusion
void function main()
    Map<string, int> ages = Map<string, int>()   // or just: Map<string, int> ages
    ages["Alice"] = 30                            // adds the key
    ages["Bob"] = 25
    ages["Alice"] = 31                            // replaces the value
    print("{@1} {@2} {@3}", ages["Alice"], ages.len(), ages.has("Bob"))
    print("{@1}", ages.get("Zed", 0))             // a default instead of an error
    for name in ages                              // the keys, in the order they were added
        print(name)

    Map<char, int> counts
    string text = "banana"
    for i in range(0, len(text))
        counts[text[i]] = counts.get(text[i], 0) + 1
    print("a: {@1}, n: {@2}", counts['a'], counts['n'])

    Dictionary<string, List<string>> groups       // the same type as Map
    groups["admins"] = ["ann"]
    groups["admins"].add("ben")
    print("{@1} {@2}", groups["admins"].len(), groups.keys().toList()[0])
```

#### A List of your own: `implements List<T>` - the core five, the rest added

<!-- example: syntax_list_implementation | task: 33.3d1 | folder: 05_collections -->
```fusion
class Ring<T> implements List<T>                      // writes the core five ...
    List<T> items
    int function len() : items.len()
    T function get(int i) : items[i]
    void function set(int i, T value)
        items[i] = value
    void function insert(int i, T value)
        items.insert(i, value)
    void function removeAt(int i)
        items.removeAt(i)

void function main()
    Ring<int> r = Ring()
    r.add(5)                                          // ... and Fusion adds the rest from them
    r.add(3)
    r.add(9)
    print("{@1} {@2} {@3}", r.len(), r.contains(3), r.indexOf(9))      // 3 true 2
    r.sortBy(func(int a, int b) : a - b)
    List<int> sorted = r.toList()
    print("{@1} {@2} {@3}", sorted[0], sorted[1], sorted[2])            // 3 5 9
    print("{@1}", r.filter(func(int x) : x > 4).len())                 // 2
    List<int> xs = Ring()                             // a List<int> holding one (33.3d2): T from the List
    xs.add(4)
    xs[0] = 6                                         // set back through Ring's set
    for x in xs
        print("{@1}", x)                              // 6
    print("{@1}", len(xs))                            // 1
```
A class implementing `List<T>` writes the core five - `len()`, `get(i)`, `set(i, v)`, `insert(i, v)`, `removeAt(i)`
(D.174); Fusion adds every other List method it doesn't write, built from them: `add`, `contains`, `indexOf`,
`remove`, `clear`, `toList`, `copyPart` / `copyPartAt` / `slice` / `sliceAt`, `filter`, `sortBy`. A class may write
any of them itself to do better (a faster `contains`). `map`, `reduce`, `sort` and `join` aren't added - the class
writes them if it needs them. Inside the class, `get` and `set` are called `this.get(i)` / `this.set(i, v)` (they are
words of `property`). A `List<int>` variable, parameter or field may hold one (D.175) - `List<int> xs = Ring()`, its
type from the List - and then everything a List does works on it: `xs[i]`, `xs[i] = v`, `foreach`, `len(xs)`, `==`,
`+`, `map`, `join` ... Each List operation checks which List it is - Fusion's own goes the direct way as before;
reading many at once from a List of your own works on a copy.

#### Raw bytes: `byte` and `bytes`

<!-- example: syntax_bytes | task: 18.3.8 | folder: 03_strings -->
```fusion
void function main()
    bytes data = toBytes("kkkkk")                 // a string's raw (UTF-8) bytes
    data[2] = 0x69                                // edit one byte in place: kkikk
    data[3] = toByte(fromHex("6A"))               // toByte checks 0-255: kkijk
    print("{data} = {@1}, {@2} bytes", toString(data), len(data))   // plain hex, nothing added

    bytes n = toBytes(258)                        // an int's 4 bytes, little-endian
    print("{n} {@1} {@2}", getInt(n, 0), rawToHex(toBytes(258, true)))   // true = big-endian
    bytes raw = [0x00, 0xFF]                      // a literal stored as bytes
    raw = raw + 0x41                              // append one byte
    setInt16(raw, 0, 513)                         // write a number inside the bytes
    print("{raw} {@1} {@2}", getUInt16(raw, 0), isText(raw))
    print("{@1} {@2}", rawToHex(slice(data, 1, 3)), indexOf(data, toBytes("ij")))
```

#### Methods: `name.toUpper()`, `String.toUpper(name)`

<!-- example: syntax_methods | task: 18.3.7 | folder: 08_classes -->
```fusion
struct Person
    string name
    int age

void function main()
    string name = "  ada lovelace  "
    print(toUpper(name))                              // the plain function still works
    print(name.trim().toTitle())                      // a method - and methods chain
    print("Claude".toUpper())                         // on text written in the source
    print(String.replace("a-b-c", "-", "+"))          // through the class
    Person p = Person("grace", 85)
    print("{@1} {@2}", p.name.capitalize(), p.age.toString().padLeft(5, '0'))
    print("{@1} {@2} {@3}", 255.toHex(), Int.parseInt("ff", 16), 'A'.charCode())
    bytes data = "kkkkk".toBytes()
    data[2] = 0x69
    print("{@1} {@2}", data.rawToHex(), data.toString())
```

#### Length: `len` and `length`, with or without brackets

<!-- example: syntax_length | task: 30.8 | folder: 04_arrays -->
```fusion
void function main()
    string name = "Ada"
    int[] scores = [90, 75, 60]
    List<string> tags = ["new", "sale"]
    Map<string, int> stock
    stock["apples"] = 3
    print("{@1} {@2} {@3} {@4}", len(name), name.len(), name.length(), name.length)
    print("{@1} {@2} {@3}", scores.length, tags.len, stock.length())   // all the same as len(x)
    if name.length > 2
        print("long name")
```

#### Classes: objects shared by reference

<!-- example: syntax_classes | task: 32.10b | folder: 08_classes -->
```fusion
class Engine
    public string kind                  // fields are private unless written public
    constructor(string kind)            // or Engine(string kind) - the same
        this.kind = kind

class Car
    public string name
    public int speed = 10
    public Engine engine                // an object: null until set
    int trips                           // private - only Car's own functions use it

    constructor(string name)
        this.name = name
        engine = Engine("V8")           // a field's bare name means this.engine

    constructor(string name, int speed) // several constructors - chosen by the values given
        this(name)                      // first line: another constructor makes the object
        this.speed = speed

    void function drive()               // functions are public unless written private
        speed = speed + 5
        count()

    private void function count()
        trips = trips + 1

class Note                              // no constructor: Note() - every field at its default
    public string text

void function main()
    Car mine = Car("Honda")             // new Car("Honda") is the same
    Car fast = Car("BMW", 90)           // the second constructor
    print("{fast.name} {fast.speed}")   // BMW 90
    Car same = byRef mine               // the same car, borrowed (Car b = mine hands it over)
    same.drive()
    print("{@1}", same == mine)         // true - the same object
    print("{mine.name} {mine.speed} {mine.engine.kind}")   // Honda 15 V8
    Car none                            // null
    if none is null
        print("no car")
    Note n = Note()
    print("[{n.text}]")                 // []
```
In a class, fields are private and functions and constructors public unless written
otherwise (`mine.trips` outside Car is an error); at module level, structs, classes and enums
are public, functions and module variables private (files/Classes.md section 1). An object is
freed when the last place holding it lets go (files/Object_Lifetime.md). `.` on null is a NullError
that `catch` handles. Two objects that hold each other (`a.friend = b` and
`b.friend = a`) are never freed: a class that can hold itself gets a warning, and setting
one of the fields to null breaks the circle (Weak references come with Task 38).

#### Statics: set up in three forms, before main

<!-- example: syntax_statics | task: 32.2c | folder: 08_classes -->
```fusion
class Car
    public string name
    public int speed
    public static int made                              // one for the whole program
    public const static Car BASIC = new Car("Basic")    // form A - direct
    public const static Car FAST = new Car("Fast") {    // form B - sets up FAST only
        FAST.speed = 200
    }
    public const static Car SPECIAL                     // given its value in form C
    static {                                            // form C - any static of Car
        SPECIAL = new Car("Special")
        BASIC.speed = 50
    }

    constructor(string name)
        this.name = name
        made = made + 1                                 // a static's bare name inside Car

    static string function summary() : format("{@1} cars made", made)   // no `this`

void function main()
    print("{Car.BASIC.name} {Car.BASIC.speed} / {Car.FAST.speed} / {Car.SPECIAL.name}")
    print(Car.summary())                                // 3 cars made
```
Form A runs first, then B, then C - each top to bottom - before `main`; a class whose set-up
uses another class is set up after it, and two that need each other are a compile error that
shows the chain (`Factory can't use Car - Car is still being set up (Car -> Engine -> Factory
-> Car)`). A const static is set only in its class's set-up. Statics are freed last.

#### Form B on any variable: a block right after the value

<!-- example: syntax_setup_blocks | task: 32.2d | folder: 08_classes -->
```fusion
class Engine
    public string kind = "none"
    public int power

class Car
    public int speed = 5
    public Engine engine = new Engine() {      // a field: every constructor runs this first
        engine.kind = "V6"
        engine.power = 300
    }

void function main()
    Car mine = new Car() {                     // a local
        mine.speed = 99
        mine.engine.power = 320
    }
    List<string> names = List<string>() {      // a List
        names.add("Ann")
        names.add("Bob")
    }
    print("{mine.speed} {mine.engine.kind} {mine.engine.power}")
    print(format("{@1} names", names.length()))
```
The block sets up that variable only - changing another variable in it is a compile error
(`The set-up block of 'mine' can only change 'mine' - change 'other' after the block`). A
class field's value may be any expression; each constructor sets it, then runs its block,
before its own body.

#### readonly parameters: read, never changed

<!-- example: syntax_readonly | task: 32.2e | folder: 11_ownership -->
```fusion
class Account
    public int balance
    void function deposit(int amount)
        balance = balance + amount

void function report(readonly Account a, readonly List<int> moves)
    print(format("balance {@1}, {@2} moves", a.balance, moves.length()))
    List<int> sorted = byVal moves              // a copy may change
    sorted.sort()
    // a.balance = 0      - error: 'a' is readonly - report may read it but not change it
    // a.deposit(5)       - error: report calls deposit, which changes a

void function main()
    Account acc = Account()
    acc.deposit(40)
    List<int> moves = List<int>()
    moves.add(40)
    report(acc, moves)
```
A readonly parameter can't be changed in any way: assigned, through a field or element, by a
List / Map method or a method that changes its object, or by passing it to a function that
changes it (the compiler follows the calls). A variable that shares it is readonly too;
keeping it in a field or List, or returning it, is an error. A const or let may still be
changed by its own set-up block (`const Point p = Point(1, 2) { p.x = 5 }`).

#### Printing an object: its class name (until ToString)

<!-- example: syntax_object_text | task: 32.2f | folder: 08_classes -->
```fusion
class Car
    public string name = "Honda"

void function main()
    Car mine = Car()
    Car none = null
    print("{mine} / {none}")                  // Car / null
    print(toString(mine))                     // Car
    print(mine.name)                          // Honda - its fields print as usual
```
A class that doesn't implement ToString prints as its class name, and the compiler warns once
per class: `Car doesn't implement ToString - it prints as its class name 'Car'`. A null object
prints `null`. With ToString (Task 32.5b) it prints its own text:

<!-- example: syntax_to_string | task: 32.5b | folder: 03_strings -->
```fusion
class Car implements ToString
    string name
    constructor(string name)
        this.name = name
    string function toString() : "Car " + name

void function main()
    Car mine = Car("Honda")
    print("{mine}")                            // Car Honda
    print(toString(mine))                     // Car Honda
```

#### Interfaces: `interface`, `implements`, `is`, a cast in front

<!-- example: syntax_interfaces | task: 32.5a | folder: 08_classes -->
```fusion
interface Shape
    float function area()
    string function name()

class Circle implements Shape
    public float r
    constructor(float r)
        this.r = r
    float function area() : 3.0 * r * r
    string function name() : "circle"

class Square implements Shape
    float side
    constructor(float side)
        this.side = side
    float function area() : side * side
    string function name() : "square"

void function main()
    List<Shape> shapes = [Circle(1.0), Square(2.0)]
    for s in shapes
        print("{@1} {@2}", s.name(), s.area())  // each object's own function
    Shape first = shapes[0]
    if first is Circle
        Circle c = (Circle)first                 // back to the class - checked while running
        print("radius {@1}", c.r)
    try
        Square q = (Square)first                 // not a Square: a CastError
    catch CastError e
        print(e.message)                         // a Circle is not a Square
```
A class may implement several interfaces (`implements Shape, Named`), and an interface may build
on several (`interface Item implements Sized, Named`). A function with code in an interface is a
default method - only with `[interfaces] defaultMethods = true`.

#### Copies of objects: `byVal`, `Cloneable`, `nocopy`, `noshare`

<!-- example: syntax_object_copies | task: 32.5b | folder: 08_classes -->
```fusion
class Engine
    public string kind = "V8"

class Car
    public string name
    public Engine engine
    constructor(string name)
        this.name = name
        engine = Engine()

void function main()
    Car a = Car("Honda")
    Car b = byVal a                       // a new Car - and a new Engine
    b.engine.kind = "V6"
    print("{a.engine.kind} {b.engine.kind}")   // V8 V6
    Car c = byRef a                       // the same car, borrowed (Car c = a moves it)
    c.engine.kind = "V12"
    print(a.engine.kind)                  // V12
```
A class with a `nocopy` field (a connection, a lock) can't be copied unless it implements
`Cloneable` with its own `Car function clone()`, which `byVal` then calls; a `nocopy` field is set
only in a constructor or `clone()`. A `noshare` field is never handed out - `return byVal log`.

#### Moving: `[memory] ownership = "strict"`

<!-- example: syntax_moving | task: 48.1 | folder: 11_ownership -->
```fusion
class Car
    public string color
    constructor(string color)
        this.color = color

void function main()
    Car a = Car("red")
    Car b = a                     // with "move": b owns the car now
    // print(a.color) here: 'a' was moved to 'b' on line 8 - use byVal a for a copy
    a = Car("blue")               // a new value brings a back
    Car c = byVal b               // a copy: two cars
    c.color = "green"
    print("{a.color} {b.color} {c.color}")   // blue red green
```
A List, a Map, an object and a struct holding one move; numbers, strings and plain structs
are copied. Moving in only one branch of an `if`, or in a loop without a new value each
pass, is an error where the name is used next. "move" is the default (D.102); `"share"`
keeps two names on one object.

#### Borrowing: passing, elements, for loops

<!-- example: syntax_borrowing | task: 48.2 | folder: 11_ownership -->
```fusion
class Car
    public string color
    constructor(string color)
        this.color = color

class Garage
    public Car car
    void function park(Car c)          // keeps c in a field: park takes it (D.100)
        this.car = c

void function paint(Car c)             // only changes c: a borrow
    c.color = "blue"

string function colourOf(readonly Car c)
    Car seen = c                       // readonly: a local borrows it (Car c: colourOf would keep c - D.172)
    return seen.color

void function main()
    List<Car> fleet = [Car("red"), Car("white")]
    Car first = fleet[0]               // a borrow: fleet is frozen while 'first' is used
    paint(first)                       // passing borrows: first is back after the call
    print(first.color)                 // blue - the last use of 'first'
    fleet.add(Car("black"))            // fine: the borrow has ended
    Garage g = Garage()
    Car mine = Car("green")
    g.park(mine)                       // with "move": mine is moved into the garage
    // print(mine.color) here: 'mine' was moved to 'park' (which keeps it) on line 26
    for c in fleet
        print(c.color)                 // c borrows each car; g.car = c would be an error
    print("{@1} cars, {g.car.color} parked", fleet.len())
    print(colourOf(fleet[1]))          // white - lent, fleet unchanged
```
With `"strict"`: passing a value lends it for the call, unless the function keeps it (stores,
adds or returns it, or gives it to a local: `Car x = c` - D.172) - then the call moves it, and `c` after
`Car x = c` is an error. A `readonly` parameter, `byRef c` and `byVal c` stay a borrow or a copy. An element or a field read into a local, and a
for loop's variable, borrow: the owner can't change until the borrow's last use, and a borrow
can't be stored or returned (`byVal` copies it). A field or an element can't be moved out.

#### One writer, and storing `this`

<!-- example: syntax_one_writer | task: 48.7 | folder: 11_ownership -->
```fusion
class Car
    public string name
    constructor(string n)
        this.name = n

    void function register(List<Car> a, List<Car> b)
        a.add(this)                    // storing this shares the car - one car in both (D.103)
        b.add(this)

void function main()
    List<Car> fleet = [Car("Mini"), Car("Golf")]
    Car first = fleet[0]               // first borrows from fleet
    first.name = "Cooper"              // first is the one writer
    print("{@1} cars", fleet.len())    // reading fleet meanwhile is fine (D.123)
    // fleet.removeAt(0) here: 'fleet' can't change while 'first' borrows from it
    print(first.name)                  // Cooper - the last use of 'first'

    List<Car> forSale = List<Car>()
    List<Car> sold = List<Car>()
    Car c = Car("Polo")
    c.register(forSale, sold)
    sold[0].name = "Polo GTI"
    print(forSale[0].name)             // Polo GTI - the same car
    Car none = null
    if none is null                    // a null check: nothing registered
        print("no car")
    try
        none.register(forSale, sold)   // no check: a NullError, caught
    catch e
        print("caught")
```
With `[memory] ownership = "strict"`: while a borrow changes a value, the owner may still be
read, but changing it another way is an error until the borrow's last use. A method that
stores `this` shares the object: every collection holds the same one, and it is freed when the
last holder lets go. With `"relaxed"` neither rule applies - the before / after table:
[files/Ownership.md](Ownership.md) section 1.

#### At the call: `readonly`, `byVal`, `byRef`

<!-- example: syntax_at_the_call | task: 48.3 | folder: 02_functions -->
```fusion
class Account
    public int balance = 5
    public int logged = 0

void function show(Account a)          // only reads a
    print("balance {a.balance}")

void function log(Account a)           // changes a
    a.logged = a.logged + 1

void function main()
    Account acc = Account()
    show(readonly acc)                 // the caller's demand: show must not change acc
    // log(readonly acc) here: log changes 'a' (line 9) - 'acc' is passed readonly; pass byVal acc for a copy
    log(byVal acc)                     // log changes a copy
    print("logged {acc.logged}")       // logged 0
    log(acc)                           // a borrow: log may change it, then hands it back
    log(byRef acc)                     // the same, written out
    print("logged {acc.logged}")       // logged 2
```
`readonly` at a call is checked through every call the function makes; when it changes or
keeps the value there are two errors - at the call, and at the line that changes it, naming
the call. `byRef` works on a List, a Map and an object. With `[memory] ownership = "strict"`,
`byRef` / `readonly` only lend: given to a function that keeps its parameter, they are an
error, and `Car b = byRef a` is a local borrow.

#### A getter lends: its result borrows from the object

<!-- example: syntax_getters | task: 48.9 | folder: 08_classes -->
```fusion
class Engine
    public string kind
    constructor(string kind)
        this.kind = kind

class Car
    public Engine engine = Engine("V8")
    Engine function getEngine() : this.engine     // returns its own field: a borrow of the car

void function main()
    Car car = Car()
    Engine e = car.getEngine()         // e borrows from car - car is frozen while e is used
    e.kind = "V6"                      // a change through the borrow reaches the car
    print(car.engine.kind)             // V6 - e's last use is over, car may be used again
    Engine spare = byVal car.getEngine()   // a copy, to keep
    car.engine = Engine("V12")
    print("{spare.kind} {car.engine.kind}")    // V6 V12
```
A function returning a part of its object (or of a parameter it borrows) lends from it - so
does one returning a new object made with such a part, like an iterator holding its
collection (D.109). The result can't be stored or returned elsewhere; `byVal` copies it.

#### A readonly result, and a deep `const`

<!-- example: syntax_readonly_result | task: 50 | folder: 11_ownership -->
```fusion
class Engine
    public int power = 90
    void function tune()
        this.power = 100

class Car
    public string name = "Mini"
    public Engine engine = Engine()
    public readonly Engine function getEngine()   // the caller may read it, not change it
        return this.engine
    void function rename(string n)
        this.name = n

void function main()
    Car car = Car()
    Engine e = car.getEngine()           // a read-only borrow of car's engine
    print("{@1}", e.power)               // 90 - reading is fine
    // e.tune() here: 'e' holds the readonly result of getEngine - tune changes it
    Engine mine = byVal car.getEngine()  // a copy - it may change
    mine.tune()
    print("{@1}", mine.power)            // 100
    const Car frozen = Car()
    print(frozen.name)                   // Mini - reading is fine
    // frozen.rename("Golf") here: 'frozen' is const - rename changes it
    Car other = byVal frozen             // a copy may change
    other.rename("Golf")
    print(other.name)                    // Golf
```
`readonly` before a function's result type is part of its signature: the caller gets a read-only
borrow and follows the readonly rules - no field set, no method or function that changes it, not
kept; `byVal` gives a copy that may change, `byRef` is an error. A readonly number or string result
is a copy, so `readonly` does nothing there (a warning). `const` on an object is deep: nothing in it
may change, except in its own set-up block. Every case: files/Ownership.md "Truth table 4b".

#### The null guard: `?.` and `??`

<!-- example: syntax_null_guard | task: 52.8 | folder: 10_errors_and_null -->
```fusion
class Person
    public string name
    public int age
    public Person spouse
    constructor(string n, int a)
        this.name = n
        this.age = a
    void function greet()
        print("hi {name}")

void function main()
    Person nobody = null
    Person ann = Person("Ann", 30)
    ann.spouse = Person("Bob", 31)
    nobody?.greet()                          // skipped - nobody is null
    ann?.greet()                             // hi Ann
    int age = nobody?.age ?? -1              // -1 - ?? gives the default
    print("{@1}", age)
    if ann?.age >= 18                        // a guarded test is false on null (a warning: D.116)
        print("adult")
    if nobody is null                        // null on its own path - never !(nobody?.age >= 18)
        print("ask for ID")
    string partner = ann?.spouse?.name ?? "none"   // every link checked
    print(partner)                           // Bob
    Person someone = nobody ?? Person("New", 1)    // the object, or the default
    print(someone.name)                      // New
```
`?.` reads through an object that may be null: a call is skipped, a test in a condition is false,
and a value needs a default you write with `??` - `int a = nobody?.age` alone is an error (nothing
changes silently). `!` around a `?.` test is an error - it would turn "unknown" into "yes"; test null
on its own (D.116; `[conditions] notAroundGuard = true` allows it with a warning). An object surely
null when passed (`Car c = null` then `drive(c)`) is an error too (D.117). Before `?.` stands a variable or a field path - after a call, store the result
first. A string, array, List or Map is never null, so `?.` on one does nothing (a warning).

#### `Default`: an object that is never null

<!-- example: syntax_default | task: 32.5b | folder: 08_classes -->
```fusion
class Settings implements Default
    public int size = 3
    private constructor()                 // may be private - the compiler calls it
        size = 5

void function main()
    Settings s                            // made when declared: Settings()
    s.size = 9
    s = null                              // the old one goes, a new default one comes
    print("{@1}", s.size)                 // 5
```

#### Inheritance: `inherits`, `override`, `super`, `typeOf`

<!-- example: syntax_inheritance | task: 32.7 | folder: 08_classes -->
```fusion
class Person
    public string name
    constructor(string name)
        this.name = name
    string function greet() : "Hi, I am " + name

class Employee inherits Person           // `extends` too - one parent only
    constructor(string name)
        super(name)                      // the parent's constructor, first
    override string function greet() : super.greet() + " and I work"

void function main()
    Person p = Employee("Bob")
    print(p.greet())                     // Hi, I am Bob and I work - the object's own
    print(typeOf(p))                     // Person.Employee
```
`abstract class` can't be made and `abstract` functions must be given below; `sealed` stops a
class being inherited or a function overridden; `protected` is for the class and the classes
below it. Fusion favours holding an object (composition) over inheritance.

#### `foreach`, and a collection of your own: `Collection<T>`, `Iterator<T>`

<!-- example: syntax_foreach | task: 32.4 | folder: 05_collections -->
```fusion
void function main()
    List<string> names = ["Ann", "Bob"]
    foreach (string n in names)           // or: foreach n in names
        print(n)
    int[3] scores = [7, 8, 9]
    foreach s in scores
        write("{s} ")
    print("")
    // names.add("Cy") inside the loop would be a compile error - build a new List instead
```
A List is a `Collection<T>` value too (Task 32.6) - its own functions answer:

<!-- example: syntax_list_collection | task: 32.6 | folder: 05_collections -->
```fusion
int function total(Collection<int> c)       // any Collection<int> - a List, or a class of your own
    int sum = 0
    foreach n in c
        sum = sum + n
    return sum

void function main()
    List<int> xs = [1, 2, 3]
    Collection<int> c = byRef xs            // the same List, borrowed
    c.add(4)
    print("{@1} {@2}", total(xs), xs.len())  // 10 4
```

A class of your own can be looped over: `class Team implements Collection<Person>` gives
`Iterator<Person> function iterator()` (a new one each time) and the other Collection functions
(add, remove, length, isEmpty, contains, addAll, removeAll, keepOnly, clear); the iterator
`implements Iterator<Person>` with `bool function hasNext()` and `Person function next()`.

#### A struct holding an object

<!-- example: syntax_struct_objects | task: 32.6 | folder: 07_structs -->
```fusion
class Person
    public string name
    constructor(string name)
        this.name = name

struct Record
    int id
    Person person                         // an object: null until set
    List<int> scores                      // never null - empty

void function main()
    Record r
    if r.person is null
        r.person = Person("Ann")
    Record copy = byVal r                 // a copy: its own Person and List (r alone would move)
    copy.person.name = "Bo"
    print("{r.person.name} {copy.person.name} {@1}", r.scores.len())   // Ann Bo 0
```

#### Commas between struct fields

<!-- example: syntax_struct_commas | task: 32.12 | folder: 07_structs -->
```fusion
struct Point { int x, int y }             // on one line: commas between the fields

struct Size
    int w                                 // on new lines: no comma needed
    int h

void function main()
    Point p = Point(1, 2)
    Size s = Size(3, 4)
    print("{@1} {@2} {@3}", p.x + p.y, s.w, s.h)
```

#### Methods inside a struct (`[structs] functions = true`)

<!-- example: syntax_struct_methods | task: 32.1 | folder: 07_structs -->
```fusion
struct Counter
    string name
    int count

    void function add(int n)            // this is the struct itself - the caller's one
        count = count + n               // a field by its bare name (or this.count)

    void function reset()
        count = 0

    string function show() : format("{@1}: {@2}", name, count)

void function main()
    Counter c = Counter("clicks", 0)
    c.add(3)
    c.add(2)
    print(c.show())                     // clicks: 5
    c.reset()
    print(c.show())                     // clicks: 0
```
Off by default (structs hold values); `examples/07_structs/fusion.toml` turns it on for this example.

#### A struct building on a struct: `implements` (or `extends` / `includes`)

<!-- example: syntax_struct_parents | task: 32.8 | folder: 07_structs -->
```fusion
struct Person
    string name
    string tel

    void function greet()
        print("Hi {name}")

struct Employee implements Person       // Person's fields first, then its own
    string employeeID
    string tel                          // Person has tel too: a warning, both kept

void function welcome(Person p)         // an Employee can go here - its Person part
    p.greet()

void function main()
    Employee e = Employee("Jeff", "082", "E7", "011")
    e.name = "Jeffrey"                  // Person's field
    e.Employee.tel = "012"              // a name both have needs the struct's name
    e.greet()                           // Person's method
    welcome(e)
    print("{e.Person.tel} {e.Employee.tel}")
```
`welcome` gets a copy of the Person part only. The method `greet` needs `[structs] functions`.

#### A whole struct as text, and `toCSV`

<!-- example: syntax_struct_text | task: 32.13 | folder: 07_structs -->
```fusion
struct Point
    int x
    int y

struct Person
    string name
    int age
    Point home

void function main()
    Person ann = Person("Ann", 30, Point(1, 2))
    print("{ann}")                      // name : "Ann",age : 30,home : {x : 1,y : 2}
    print(ann.toCSV())                  // a heading row, then a row of values
    Person[] team = [ann, Person("Bo", 41, Point(3, 4))]
    print(team.toCSV(";"))              // one heading row, one row per person
```
Prints:
```
name : "Ann",age : 30,home : {x : 1,y : 2}
Person.name,Person.age,Person.home.x,Person.home.y
"Ann",30,1,2
Person.name;Person.age;Person.home.x;Person.home.y
"Ann";30;1;2
"Bo";41;3;4
```
`toCSV` works on any struct, a one-dimensional array or a `List` of structs; the delimiter is
`","` when left out. A field both a struct and the one it builds on have is printed with its
struct's name (`Person.tel : "082",...,Employee.tel : "011"`).

#### Your own functions as methods: `p.moved(1, 2)` is `moved(p, 1, 2)`

<!-- example: syntax_functions_as_methods | task: 44.2 | folder: 02_functions -->
```fusion
struct Point
    int x
    int y

Point function moved(Point p, int dx, int dy) : Point(p.x + dx, p.y + dy)
int function twice(int n) : n * 2

void function main()
    Point p = Point(1, 2)
    Point q = p.moved(10, 20).moved(1, 1)     // any function, on its first argument - chained
    print("{p.x} {p.y} -> {q.x} {q.y}")       // p is unchanged: the function got a copy
    print("{@1}", 21.twice())                 // on built-in values too
```
List / Map methods (`xs.add`) and an enum's `toString` / `toInt` come first. A struct holds
values only - a function inside a struct is a later `fusion.toml` option (off by default).

#### Modules and `import` (several files - not built as a single example)

```text
shop/
  main.fusion          <- the program
  money/price.fusion   <- module money: every .fusion file in the folder
  money/format.fusion
  geometry/shapes/area.fusion   <- module geometry.shapes
```
```fusion multi-file
import money                    // money.make(5), money.Price
import money.Price              // Price, without a prefix
import geometry.shapes          // the last part of the path: shapes.square(4)
import lib.utils as libutils    // an alias

void function main()
    money.Price p = money.make(1999)
    print("{@1} {@2}", money.show(p), shapes.square(4))
```
```fusion multi-file
// money/price.fusion - only `public` names can be used by other modules
public struct Price
    int cents
public Price function make(int cents) : Price(cents + fee())
internal int function fee() : 50 // only module money (or its namespace) sees it
```
Who can use what (Task 32.2h): `public` - everyone; `internal` - the namespace (a file
without one: its module); `private` - the class (a member only; on a top-level item it is an
error). Nothing written: fields and module variables private, everything else public.
```fusion multi-file
namespace Shop                   // the first line: shop modules see each other's internal names
import stock

class Till
    internal int drawer          // the Shop namespace may use it
    private int secret           // Till's own functions only
```
Each file imports what it uses; files of one module share all their names; each module is
loaded once, so modules may import each other. A whole project to try: `examples/13_projects/shop/`.
`python main.py main.fusion --interface` prints the public names of every module it imports - a parameter the
function keeps marked `Car c (kept)` (a call moves the argument, D.100), a readonly one `readonly Car c`.

#### Errors: `T, Error function`, capturing an error

<!-- example: syntax_errors | task: 26.2 | folder: 10_errors_and_null -->
```fusion
struct Ship
    string name
    int crew

Ship, Error function loadShip(string name)   // `, Error` marks it as able to fail -
    if name == ""                            // optional: any function may return an Error
        return Error("No name given", 400)   // a message, and optionally a code
    return Ship(name, 3)

Error function save(Ship s)                  // can fail, returns no value
    if s.crew > 2
        return Error("Too many crew on {s.name}")

void function main()
    Ship s, err = loadShip("")               // capture the error (`Error err` also works)
    if err                                   // true when there is one
        print("{err} (code {@1}, at {@2})", err.code, err.where)
    Ship ok, Error none = loadShip("Dawn")
    print("{ok.name}, no error: {@1}", not none)
    Error e = save(ok)                       // capture works on any call
    print("save: {e}")
    Ship last = loadShip("Last")             // not captured: an error would bubble up -
    print(last.name)                         // at main the program stops with its message
```

#### Whole numbers: overflow and wrapping

<!-- example: syntax_overflow | task: 27.2b | folder: 01_basics -->
```fusion
int function hash(string text)
    int h = 17
    unchecked                                // + - * inside wrap around on purpose
        for c in [1, 2, 3]
            h = h * 1000003 + c
    return h

void function main()
    int big = 2147483647
    try
        print("{@1}", big + 1)               // doesn't fit in an int: an OverflowError
    catch OverflowError e                    // (an ArithmeticError) - never a changed value
        print("{e}")
    print("{@1} {@2}", wrapAdd(big, 1), big.wrapMul(2))   // wrapping on purpose
    print("{@1} {@2}", hash("x"), 60 * 60 * 24)            // written numbers: no check
```
`[numbers] overflowWrap = true` in fusion.toml makes all `+ - *` wrap (array bounds stay checked).

#### Custom error types

<!-- example: syntax_error_types | task: 26.9 | folder: 10_errors_and_null -->
```fusion
error ConfigError : FileError                // a custom error, extending Fusion's FileError:
    int line                                 // every Error field, FileError's path, its own
    int attempts = 1

error MissingConfig : ConfigError            // extends another error type
    message = "Config file not found"        // a default message (code = ... works too)

int function load(string path)
    if path == ""
        throw MissingConfig(path = "app.cfg", line = 0)   // message, code, then fields
    return 1

void function main()
    int n, ConfigError err = load("")        // a MissingConfig is a ConfigError too
    print("{err}: {err.path} line {err.line} (attempt {err.attempts}, n = {n})")
    ConfigError made = ConfigError("Bad value", 5, "app.cfg", 12)
    Error any = made                         // every error type is an Error
    print("{any} / {made.path} / code {@1}", made.code)
    match any                                // match on error types (a typo is a compile error)
        case MissingConfig: print("gone: {any.path}")   // inside, any is a MissingConfig
        case ConfigError: print("{any.kind}: line {any.line}")   // kind: the type's name
        else: print("something else")
    try
        load("")
    catch MissingConfig e                    // the first catch whose type matches takes it
        print("missing: {e.path}")
    catch e                                  // any other error - an untyped catch goes last
        print("{e.kind}: {e}")
    List<int> xs = [1, 2]
    try
        print("{@1}", xs[5] / 0)             // Fusion's own failures have types too
    catch LookupError e                      // IndexError, KeyError
        print("{e.kind}: {e}")
    catch ArithmeticError e                  // DivideByZeroError
        print("{e.kind}: {e}")
```

#### `try` / `catch` / `finally` / `throw`

<!-- example: syntax_try | task: 26.3 | folder: 10_errors_and_null -->
```fusion
int, Error function half(int n)
    if n % 2 == 1
        return Error("odd: {n}", 7)
    return n / 2

void function main()
    for n in [4, 3, 8]
        try                                  // an error in here goes to the catch
            print("{n} / 2 = {@1}", half(n))
        catch err                            // err: the Error
            print("caught: {err} (code {@1})", err.code)
            if err.code == 7
                continue                     // the finally still runs first
        finally                              // always runs
            print("done with {n}")
    try
        throw Error("stop here")             // throw works in any function
    catch err
        print("caught: {err}")
    int n, Error bad = toInt("12x")          // a built-in's failure is an Error too
    List<int> xs = [1, 2]
    try
        print("{@1}", xs[5])                 // index out of range, a missing file, ...
    catch err
        print("{bad} / {err}")
```

#### Equality: `=`, `==`, `!=`, `===`, `!==`

<!-- example: syntax_equality | task: 18.3.5 | folder: 01_basics -->
```fusion
struct Point
    int x
    int y

void function main()
    int x = 2
    if x = 2                            // inside a condition `=` compares, like `==`
        print("x is 2")
    if x == "2" and 'a' == "a" and x == 2.0
        print("== compares values across a few types")
    if x !== "2"                        // === and !== also compare the type
        print("2 and \"2\" are different types")
    Point a = Point(1, 2)
    if a == Point(1, 2)
        print("structs compare field by field")
    int[3] n = [1, 2, 3]
    if n == [1, 2, 3] and n != [3, 2, 1]
        print("arrays compare element by element")
```

#### Project settings - `fusion.toml` (optional, next to the source file)

`fusion.toml` is the default; `fusion.yaml`, `fusion.json` or `fusion.ini` work too (Task 31).
With no settings file, the compiler writes a `fusion.toml` with every setting at its default.
Every setting and its values: `files/fusionSettings.xml`.

```toml
[project]
fusionSettingFormat = "TOML"     # TOML / YAML / JSON / INI - change it and the next compile
                                 # rewrites the file in that format (the old one kept as .bak)

[indentation]
tabWidth = 4
allowMixed = true

[source]
allowUnicodeIdentifiers = false
caseSensitive = true            # false: names that differ only in case (count / Count) are an error

[strings]
encoding = "utf-8"               # utf-8 (default) | ascii - also named: utf-16, utf-32 (future)
maxLength = "max"               # no limit (default); a number = longer strings are an error
nullBecomesEmpty = false         # a string is never null: s = null is an error | true: s becomes ""

[stdlib]
layer = "std"                    # std (default) | alloc (no OS: no print, files) | core (no heap)

[memory]
ownership = "strict"             # strict (default): Car b = a hands it over, every rule | relaxed: shares
                                 # (was assignment = "move" | "share" - still read, with a warning)
moveFieldOut = false             # true: a field may leave a struct you own; the struct is then gone

[modules]
variables = true                 # module-level variables (constants are always allowed)

[visibility]
required = false                 # true: public / internal / private written everywhere

[interfaces]
defaultMethods = false           # true: an interface's function may have code (a default)

[collections]
allowChangeWhileLooping = false  # true: a collection class of your own may change inside a loop over it

[arrays]
stackWarn = "16KB"               # an array on the stack larger than this: a warning (bytes - "512B", "1MB")
stackLimit = "64KB"              # larger than this: a compile error - use int:[] or a List (heap)
order = "columns"                # m[r][c][d]: loops and length go depth -> columns -> rows; "rows": as C;
                                 # "depthRows": depth -> rows -> columns
storage = "flat"                 # 2 or 3 dimensions in one block; "rect" comes later; JAGG per array (setStorage)

[conditions]
numbers = "positive"             # if / while count: count > 0 (default); "nonzero": count != 0;
                                 # "off": a condition must be a bool

[numbers]
overflowWrap = false             # true: whole-number + - * wraps (255 + 1 in a byte is 0)
autoWidening = false            # an int used as a float must fit exactly (else an error);
                                 # true: it widens automatically, with a warning

[errors]
returns = true                   # T, Error function / capturing errors (default on)
exceptions = true                # try / catch / finally / throw (default on)

[structs]
maxNestingDepth  = 3
warnNestingDepth = 3
stringStorage     = "owned"
stringMutable     = true
stringWarnLength = 64
holdCollections   = true        # a struct field may be a List / Map; false: an error

[build]
waitAtExit = false             # true: wait for a key before the window closes (development,
                                 # examples, testing) - each examples/ topic folder's fusion.toml turns it on

[safety]
mode = "safe"                    # safe (default) | strict (every warning is an error) | unsafe
maxCallDepth = "max"           # endless recursion: caught by stack use; a number also counts
                                 # calls (memory-constrained devices) - a StackOverflowError

[generics]
enabled = true                  # generic functions, structs and classes of your own; false: an error
sharedStatics = false           # a generic class's statics: one set per copy; true: one for all

[ranges]
strictStep = false              # a step that misses the end: a warning; true: a compile error

[backend]
target = "c"
```

#### Running

```text
python main.py program.fusion     # -> program.c and program.exe
python check.py                   # tests, examples, leak check, ASCII, this file
```

#### Reserved words

```text
if else for while loop End break continue return match case
function func async await
class struct interface enum inherits implements property get set
public private protected static virtual override abstract sealed
const   true false null this   and or not is in
int float double string bool char byte short long void
Unique Shared Weak   go   try catch finally throw Error
```
`end` and `var` are ordinary names (Task 44.5): a lowercase `end` closes a block only right
before a block word (`end function`), and `var` is free until type inference exists.
`template` (Task 29.3) is special only before `string` and a name; otherwise it is a name too.
