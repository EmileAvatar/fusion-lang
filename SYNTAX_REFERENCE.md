# Fusion Syntax Reference - what works today

A showcase: one short example per **implemented** feature. Every ` ```fusion ` block is a
complete program that `python check.py` compiles and runs, so this file can't drift from the
compiler. The marker above each block (`<!-- example: name | task: N -->`) names the program
`python check.py --build-examples` writes to `examples/`. Planned features are listed in `FEATURES.md`; the full design is in
`files/fusion-language-spec.md`.

When a feature ships, add its example here (Auto-Update Policy in `CLAUDE.md`).

---

#### Hello, functions and the three block styles

<!-- example: syntax_functions_and_blocks | task: 01-04 -->
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

<!-- example: syntax_variables_and_control_flow | task: 08 -->
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

#### Default parameters and named arguments

<!-- example: syntax_defaults_and_named_args | task: 18.2.2 -->
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

<!-- example: syntax_interpolation | task: 18.2.2b -->
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
```

#### Lambdas and function values

<!-- example: syntax_lambdas | task: 18.1.3 -->
```fusion
int function apply((int) : int f, int v) : f(v)
int function triple(int x) : x * 3

void function main()
    (int) : int twice = func(int x) : x * 2
    print("{@1} {@2}", apply(twice, 5), apply(triple, 5))   // named functions are values too
```

#### Arrays

<!-- example: syntax_arrays | task: 18.2.4 -->
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

<!-- example: syntax_structs | task: 18.2 -->
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

<!-- example: syntax_strings | task: 18.3.1 -->
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

#### String operations (each returns a new string)

<!-- example: syntax_string_operations | task: 18.3.2 -->
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

<!-- example: syntax_unicode | task: 18.3.2b -->
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

#### String library: inspect, search, extract, change, pad

<!-- example: syntax_string_library | task: 18.3.6 -->
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
    print("{@1} {@2}", truncate("Hello world", 8), truncate("Hello world", 6, "~"))
```

#### Equality: `=`, `==`, `===`

<!-- example: syntax_equality | task: 18.3.5 -->
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
    if x !== "2"
        print("=== also compares the type")
    Point a = Point(1, 2)
    if a == Point(1, 2)
        print("structs compare field by field")
    int[3] n = [1, 2, 3]
    if n == [1, 2, 3] and n != [3, 2, 1]
        print("arrays compare element by element")
```

#### Project settings - `fusion.toml` (optional, next to the source file)

```toml
[indentation]
tab_width = 4
allow_mixed = true

[source]
allow_unicode_identifiers = false

[strings]
encoding = "utf-8"               # utf-8 (default) | ascii - also named: utf-16, utf-32 (future)
max_length = "max"               # no limit (default); a number = longer strings are an error

[structs]
max_nesting_depth  = 3
warn_nesting_depth = 3
string_storage     = "owned"
string_mutable     = true
string_warn_length = 64

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
