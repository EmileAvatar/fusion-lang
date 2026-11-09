[< 052 Interfaces](052-Interfaces.md) | [Index](index.md) | [061 Enums >](061-Enums.md) <!-- nav -->

# 060 Structs

Contents: [Struct Rules](#struct-rules) | [Structure Definition](#structure-definition) | [String Fields](#string-fields) | [Value Semantics](#value-semantics)

## Structures and Value Types

**Status:** [DONE 18.2, 32] fields, value semantics, nesting, string fields; Lists and Maps in a struct (32.10a);
an object in a struct (D.097); methods on structs (32.1 - `[structs] functions = true`).

**Methods (Task 32.1, built):** with `[structs] functions = true` (off by default) a struct may hold functions
- A method gets the struct as `this`, **by reference** - `p.move(1, 2)` changes `p`
- Inside, a field's bare name means `this.field` (or write `this.x`), and another method's bare name
  `this.method(...)`
- A parameter or local can't take a field's name, and a method can't share a field's name
- On a `const` struct only methods that don't change `this` can be called
- The struct's own method comes before a free function of the same name (44.2)
- In C a method is a function whose first parameter is a pointer to the struct

```
struct Point
    int x
    int y
    void function move(int dx, int dy)
        x = x + dx
        y = y + dy
    int function sum() : x + y

Point p = Point(1, 2)
p.move(3, 4)                // p is now (4, 6)
```

**Structs building on structs (Task 32.8, built):** `struct Employee implements Person` (`extends` and
`includes` mean the same)
- An Employee has Person's fields first, then its own
- The constructor takes them in that order (`Employee("Jeff", "082", "E7")`), or a whole Person first
  (`Employee(p, "E7")`), or named values
- In C the Employee holds a Person as its first member, named `Person`

- **Where a Person is expected** (a parameter, `Person p = e`, a `List<Person>`, a return)
  an Employee can be given: it becomes its Person part - a copy of that part only, so the
  receiver can use only Person's fields and methods
- **Person's methods work on an Employee:** `e.greet()` runs Person's `greet` on `e.Person`,
  by reference (it can change `e`); inside Employee's methods Person's fields and methods
  are used by their bare names
- **A field both have** (`tel`) is kept twice, with a warning; `e.tel` is then an error -
  write `e.Person.tel` or `e.Employee.tel`. A field can't have the name of a struct it builds
  on, or of a method it builds on
- A chain works the same way (`Manager extends Employee`); building on a struct doesn't count
  as nesting (`[structs] maxNestingDepth`); no struct may build on itself
- **A whole struct as text (Task 32.13):** `"{e}"` (and `format("{@1}", e)`) gives every field,
  the part it builds on first, as `name : value` joined by a comma with no space - a string
  in "", a char in '', a struct inside in braces: `name : "Jeff",age : 30,home : {x : 1,y : 2}`.
  A field both structs have is named with its struct (`Person.tel : "082"`)
- **`x.toCSV()` / `x.toCSV(";")` (Task 32.13):** on any struct, a one-dimensional array or a `List` of structs
  - one heading row naming each field by its struct (`Person.name`; a struct inside: `Person.home.x`)
  - then one row of values per struct, separated by the delimiter (default ",")
  - strings in "" with a " inside doubled; no newline after the last row
  - a struct's own `toCSV` method (or the program's own function) comes first
  - not for a struct with an array, list or map field; arrays of more dimensions: later
- Later (32.7): `typeOf(x)` gives the chain (`Person.Employee.Manager`) and a value can be
  converted back; a normal parameter holds only the Person part (`typeOf` says `Person`), a
  `byRef` one the whole struct

```
struct Person
    string name
    void function greet()
        print("Hi {name}")

struct Employee implements Person
    string employeeID

void function welcome(Person p)
    p.greet()

Employee e = Employee("Jeff", "E7")
welcome(e)                  // Hi Jeff
print("{e}")                // Jeff, E7
```

**Settings decided (user, 2026-10-24):**
- A struct is never null
- `[structs]` holding List / Map on (built)
- Functions on structs off by default (32.1)
- A struct may hold an object - null until set, shared when the struct is copied (user, 2026-11-01)

Description: Lightweight value types for copying data around an application and reading or
changing it conveniently.

**Implementation status (Task 18.2):** see `files/taskSummary2.md`
- 18.2.1 (core structs) - implemented
- 18.2.2 (named construction, `Point(y = 4, x = 3)`) - implemented
- 18.2.3 (nested structs, array fields, arrays of structs) - implemented
- Arrays as function return values (18.2.4) - implemented, see "Array return values"

---

### Struct Rules

Description: Structs are **value containers** - copied, never null (user decision, 2026-10-08; since
widened, see below).

* **Methods: off by default** - with `[structs] functions = true` a struct may hold functions
  (Task 32.1, see "Methods" above); otherwise behaviour belongs in ordinary functions that take or
  return the struct. No operator overloading, no user-written constructors
* **One generated constructor:** the compiler creates `Point(...)`, taking every field in the
  order the fields are declared, so all values can be set at once
* **Allowed field types (implemented):**
  * `int`, `float`, `double`, `bool`, `char`, `string`, `byte`, `bytes`, enums
  * other structs
  * fixed-size arrays of any of these (`int[3] scores`, `Point[4] corners` - the size is required,
    because a struct's size is fixed)
  * **Lists and Maps** (`List<string> tags`, `Map<string, int> counts`) - with
    `[structs] holdCollections = true`, the default (Task 32.10a); never null - an empty one to start
  * **an object** (`Engine engine`) - **null until set** (D.097, STC.007):
    * under `[memory] assignment = "move"` (the default) the struct moves as a whole, its object with it
    * `byVal` copies the struct and clones the object; `byRef` borrows it
    * under "share" a copied struct shares its object - an object isn't a value
* **Nesting depth** is limited per project (`[structs]` in `fusion.toml`): with the defaults,
  a struct 3 levels deep compiles with a warning and 4 levels is an error.
  `max_nesting_depth = 1` turns nested structs off; raising it allows deeper ones. Depth
  counts levels of structs - plain fields only = 1, holding such a struct = 2; an array of
  structs counts like one struct
* A struct can't contain itself, directly or through other structs (it would be infinitely
  large)
* **Not allowed:** `void`; a struct implementing an interface (STC.005 - a struct only holds values)

---

### Structure Definition

Description: Declared at the top level of a file, in any of the three block styles.

```
// Indentation style
struct Point
    int x
    int y

// Braces style, with field defaults (constants only, like parameter defaults)
struct Player {
    string name
    float health = 100.0
    int score
}

// End keyword style
struct Book
    string title
    bool available = true
End struct

// Invalid - structs can only contain fields
/*
struct Vector3
    float x
    Vector3 operator +(Vector3 other)       // ERROR: no operators in structs
    float function magnitude()               // ERROR: no functions in structs
*/
```

**Nesting (Task 18.2.3):**

```
struct Rect
    Point min
    Point max

struct Team
    string name
    int[3] scores            // array fields need a size
    Point[2] positions       // arrays of structs too

Rect r = Rect(Point(0, 0), Point(4, 3))
r.max.x = 40                 // nested field access
Team t = Team("Blue", [3, 5, 7])   // an array field takes an array literal of its exact size
t.scores[0] = 10
Point[] pts = [Point(1, 2), Point(3, 4)]   // arrays of structs
pts[0].x = 7
```

* Array and struct fields start with their own defaults (zero, `""`, or the inner struct's
  field defaults), so they can be left out of a constructor - like a field with a default -
  but can't be given a written default themselves
* Copying a struct copies everything inside it, nested structs and arrays included
* A whole array field can't be assigned at once (`t.scores = [...]`) - assign its elements
* An array field or an array of structs is passed to `int[]`/`Point[]` parameters by
  reference, like any array

**Construction and fields:**

```
Point a = Point(3, 4)              // generated constructor, fields in declaration order
Point b = Point(y = 4, x = 3)      // named: any order (see "Calling Functions" for the rules)
Player ada = Player("Ada", 75)     // trailing fields with defaults may be left off (score = 0)
Player bo = Player(score = 9, name = "Bo")   // named: any field with a default can be skipped
Point z                            // no value given: every field is its default, or zero
                                   //   (zero for numbers, false, '\0', and "" for strings)
a.x = 10                           // read and write fields with '.'
print("({a.x}, {a.y})")            // fields can be printed through interpolation
const Point ORIGIN = Point(0, 0)   // no field of a const struct can be changed
```

**Rules:**
* A struct can be used before it is declared in the file (like functions)
* A struct can't share its name with a function, another struct, or a builtin, and a
  variable or parameter can't reuse a struct's name
* Positionally, a field with a default can only be left off when no later field is given -
  every field up to the last one *without* a default is required
* With named arguments, any field with a default can be skipped
* Not supported yet, each with a clear error: comparing structs with `==`/`!=` (struct
  equality is part of Task 18.3's equality-operator design - compare fields instead),
  printing a whole struct (`print("{p}")`), arithmetic on structs

---

### String Fields

Description: A `string` field holds its own value and can be changed - not pooled, by default.
- It can hold anything from a book title to a full product description
- Strings have no length limit unless the project sets one (`[strings] maxLength`, see "String Implementation")
- Controlled per project in `fusion.toml`'s `[structs]` section (see "Project Configuration"):

* `string_warn_length` (default **64**) - a guideline only: a longer string is kept in full,
  and the compiler warns
* `string_mutable` (default `true`) - `false` makes a string field unchangeable after the
  struct is created
* `string_storage` (default `"owned"`) - `"pooled"` is reserved for Task 29 and is a compile
  error until then

A string field owns its text like any string value (see "String Implementation"), so it
holds any length, is copied with the struct and freed with it (Task 18.3.1).
`string_warn_length` stays a compile-time guideline.

---

### Value Semantics

Description: Structs are copied, not referenced - on assignment, when passed to a function,
and when returned.

```
Point pos1 = Point(10, 20)
Point pos2 = pos1           // Copied, not referenced
pos2.x = 50                 // pos1.x is still 10

void function modifyPoint(Point p)
    p.x = 100               // Modifies the function's own copy

Point original = Point(1, 2)
modifyPoint(original)
// original.x is still 1
```

Arrays are different: they are passed **by reference** (see "Array parameters").

[< 052 Interfaces](052-Interfaces.md) | [Index](index.md) | [061 Enums >](061-Enums.md) <!-- nav -->
