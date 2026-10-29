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

`print` always ends the line it prints (there is no separate `println` yet).

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

#### Module variables and constants: shared by a module's functions

<!-- example: syntax_module_variables | task: 44.1 -->
```fusion
const int LIMIT = 3                       // a module constant
int count = 0                             // a module variable - every function sees it
List<string> log = []                     // freed when the program ends

void function record(string what)
    count = count + 1
    log.add(what)

void function main()
    for i in range(0, LIMIT)
        record("step {i}")
    print("{count} steps: {@1}", log.join(", "))
```
They are set in the order written, before `main`'s own code; an initializer may use the
functions and the module variables above it. `public` lets other modules use one
(`stats.total`). A name inside a function can't hide a module variable. `[modules] variables =
false` in `fusion.toml` turns module variables off (constants stay allowed).

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
    print("\{name\} is written as \{name\}")      // \{ \} - a brace as text: {name} is written as {name}
```

#### String templates: `template string greet = "Hello {@1}"`

<!-- example: syntax_templates | task: 29.3 -->
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

<!-- example: syntax_number_conditions | task: 30.9 -->
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

<!-- example: syntax_conditional | task: 30.7 -->
```fusion
void function main()
    int count = 7
    string size = (count > 5) ? "big" : "small"      // one line, gives a value
    int band = (count > 100) ? 3 : (count > 5) ? 2 : 1
    print("{size} {band}")
    print((count % 2 == 0) ? "even" : "odd")          // only the chosen value runs
```

#### Long lines: a line break inside `( )` or `[ ]` continues the line

<!-- example: syntax_long_lines | task: 44.3 -->
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
    try
        scores[5] = 1                       // every index is checked: an IndexError
    catch IndexError e
        print("{e}")
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

#### Enums

<!-- example: syntax_enums | task: 25.2 -->
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

#### Enums can be null: an unset enum is `null`

<!-- example: syntax_null_enums | task: 30.11 -->
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

<!-- example: syntax_enum_data | task: 25.4 -->
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

<!-- example: syntax_match | task: 25.3 -->
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

<!-- example: syntax_fall_match | task: 30.13 -->
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

#### Changing a character: `s[i] = c`

<!-- example: syntax_string_put | task: 29.1 -->
```fusion
void function main()
    string a = "Andrew"
    string b = a                        // an independent copy
    b[0] = 'X'                          // changes b's own text only
    string word = "cafe"
    word[3] = '\u00e9'                  // a wider character: the rest moves along
    print("{a} {b} {word}")
    const string fixed = "Ann"          // a const string is fixed: fixed[0] = 'X' is an error
    try
        b[10] = 'z'                     // every index is checked: an IndexError
    catch IndexError e
        print("{e}")
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

#### String library: inspect, search, extract, change, pad, number bases, formatting, compare, mask

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

<!-- example: syntax_files | task: 18.5.5 -->
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

<!-- example: syntax_program_io | task: 18.5.4 -->
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

<!-- example: syntax_run | task: 28.1.1 -->
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

<!-- example: syntax_lists | task: 18.5.1 -->
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
    List<string> copy = names                     // an independent copy
    copy.add("Linus")
    Team t = Team("core", names)
    t.members.add("Ken")
    print("{@1} {@2} {@3}", names.len(), copy.len(), t.members[2])

    List<List<int>> grid = [[1, 2], [3, 4]]
    grid[1][0] = 9
    print("{@1}", grid == [[1, 2], [9, 4]])

    List<string> parts = "a,b,,c".split(",")      // every piece, empty ones too
    print("{@1} {@2}", parts.len(), parts.join(" + "))   // also join(parts, " + ")
    print("{@1} {@2}", lines("one\ntwo\n").len(), words("  the quick  fox ").join("|"))
```

#### Maps: `Map<K, V>` (also written `Dictionary<K, V>`)

<!-- example: syntax_maps | task: 18.5.2 -->
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
    print("{@1} {@2}", groups["admins"].len(), groups.keys()[0])
```

#### Raw bytes: `byte` and `bytes`

<!-- example: syntax_bytes | task: 18.3.8 -->
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

<!-- example: syntax_methods | task: 18.3.7 -->
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

<!-- example: syntax_length | task: 30.8 -->
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

#### Methods inside a struct (`[structs] functions = true`)

<!-- example: syntax_struct_methods | task: 32.1 -->
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
Off by default (structs hold values); `examples/fusion.toml` turns it on for this example.

#### Your own functions as methods: `p.moved(1, 2)` is `moved(p, 1, 2)`

<!-- example: syntax_functions_as_methods | task: 44.2 -->
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
int function fee() : 50          // private: only the files of module money see it
```
Each file imports what it uses; files of one module share all their names; each module is
loaded once, so modules may import each other. A whole project to try: `examples/shop/`.
`python main.py main.fusion --interface` prints the public names of every module it imports.

#### Errors: `T, Error function`, capturing an error

<!-- example: syntax_errors | task: 26.2 -->
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

<!-- example: syntax_overflow | task: 27.2b -->
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

<!-- example: syntax_error_types | task: 26.9 -->
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

<!-- example: syntax_try | task: 26.3 -->
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

[strings]
encoding = "utf-8"               # utf-8 (default) | ascii - also named: utf-16, utf-32 (future)
maxLength = "max"               # no limit (default); a number = longer strings are an error

[stdlib]
layer = "std"                    # std (default) | alloc (no OS: no print, files) | core (no heap)

[modules]
variables = true                 # module-level variables (constants are always allowed)

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
                                 # examples, testing) - examples/fusion.toml turns it on

[safety]
mode = "safe"                    # safe (default) | strict (every warning is an error) | unsafe
maxCallDepth = "max"           # endless recursion: caught by stack use; a number also counts
                                 # calls (memory-constrained devices) - a StackOverflowError

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
