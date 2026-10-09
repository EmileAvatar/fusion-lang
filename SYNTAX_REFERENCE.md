# Fusion Syntax Reference - what works today

A showcase: one short example per **implemented** feature. Every ` ```fusion ` block is a
complete program that `python check.py` compiles and runs, so this file can't drift from the
compiler. Planned features are listed in `FEATURES.md`; the full design is in
`files/fusion-language-spec.md`.

When a feature ships, add its example here (Auto-Update Policy in `CLAUDE.md`).

---

#### Hello, functions and the three block styles

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

#### Variables, constants, control flow

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
        print("count {count}, grade {grade}")
```

#### Default parameters and named arguments

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

```fusion
void function main()
    string name = "Ada"
    int age = 36
    print("{name} is {age}")                       // a name or a field path inside {}
    print("{@2}, {@1}!", "World", "Hello")          // any order, repeatable
    print("100% sure")                              // % is printed as-is
```

#### Lambdas and function values

```fusion
int function apply((int) : int f, int v) : f(v)
int function triple(int x) : x * 3

void function main()
    (int) : int twice = func(int x) : x * 2
    print("{@1} {@2}", apply(twice, 5), apply(triple, 5))   // named functions are values too
```

#### Arrays

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
    scores[0] = 99
    int[3] p = podium()
    print("{@1} {@2} {@3} {@4}", sum(scores), len(scores), buffer[0], p[0])
```

#### Structs (fields only, copied by value)

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

#### Strings (values, freed automatically)

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

## String operations (each returns a new string)

```fusion
void function main()
    string name = "Ada"
    string full = name + " " + "Lovelace" + '!'   // join strings (and chars) with +
    print("{full}: {@1} bytes, first {@2}", len(full), full[0])   // s[i] is bounds-checked
    print("[{@1}] [{@2}] [{@3}]", substring(full, 4, 8), toUpper(name), trim("  x  "))
    print("{@1} {@2} {@3} {@4}", contains(full, "Love"), indexOf(full, "Love"), startsWith(full, "Ada"), endsWith(full, "!"))

    string input = "42"
    if isInt(input)                                // check before converting
        int n = toInt(input)
        string text = toString(n * 2) + " / " + toString(2.5) + " / " + toString(true)
        print(text)
    // toInt("12x") would stop the program: Runtime error at file:line: '12x' is not a whole number
```

#### Project settings - `fusion.toml` (optional, next to the source file)

```toml
[indentation]
tab_width = 4
allow_mixed = true

[source]
allow_unicode_identifiers = false

[structs]
max_nesting_depth  = 3
warn_nesting_depth = 3
string_storage     = "owned"
string_mutable     = true
string_warn_length = 64
string_max_length  = 4096        # or "max memory" (unsafe)

[safety]
mode = "normal"                  # reserved

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
if else for while loop end break continue return match case
function func async await
class struct interface enum inherits implements property get set
public private protected static virtual override abstract sealed
var const   true false null this   and or not is in
int float double string bool char byte short long void
Unique Shared Weak   go   try catch finally throw Error
```
