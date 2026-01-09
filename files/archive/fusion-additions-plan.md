# Fusion Language Additions Plan

Description: Planned additions and enhancements to the Fusion language specification based on user requirements.

---

## Status Check

Description: Verification of completed work.

**Files Created**:
* ✓ fusion-language-spec.md (v2) - 64KB
* ✓ fusion-planning.md (v2) - 61KB
* ✓ fusion-summary.md - 12KB
* ✓ fusion-templates.md - 17KB
* ✓ fusion-threading-concurrency.md - 16KB

**All Previous Tasks**: ✓ Completed

---

## New Additions to Implement

Description: Features and enhancements to add to Fusion specification.

---

### 1. Enums

Description: Enumeration type for named constant values.

**Syntax Options** (User will choose preferred):

**Option 1: With Braces**
```
Enum Planets {
    MARS,
    VENUS,
    EARTH,
    JUPITER
}
```

**Option 2: Indentation-Based**
```
Enum Planets
    MARS
    VENUS
    EARTH
    JUPITER
```

**Option 3: Single-Line**
```
Enum Planets: MARS, VENUS, EARTH, JUPITER
```

**With Values**
```
Enum StatusCode {
    OK = 200,
    NOT_FOUND = 404,
    SERVER_ERROR = 500
}

// Or indentation
Enum StatusCode
    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500
```

**Usage**
```
Planets planet = Planets.MARS
StatusCode status = StatusCode.OK

if status == StatusCode.OK
    print("Success!")
```

**Features**:
* Default integer values (0, 1, 2, ...)
* Custom values supported
* Type-safe (cannot assign int directly)
* Can be used in switch/match statements

---

### 2. Comparison Operators

Description: Adding `<>` as "not equal to" operator.

**Complete Operator Set**:

Operator | Meaning | Example
---|---|---
`==` | Equal to | `a == b`
`!=` | Not equal to | `a != b`
`<>` | Not equal to (alternative) | `a <> b`
`<` | Less than | `a < b`
`>` | Greater than | `a > b`
`<=` | Less than or equal | `a <= b`
`>=` | Greater than or equal | `a >= b`

**Note**: `<>` does NOT conflict with generic type parameters because:
* Type parameters: `<T>` used in type declarations
* Comparison: `<>` used in expressions
* Parser distinguishes by context

**Example**
```
int x = 5
int y = 10

if x <> y
    print("Not equal")

// Both work the same
if x != y
    print("Not equal")

// No confusion with generics
List<int> numbers = List<int>()
if numbers.length <> 0
    print("Has elements")
```

---

### 3. Comments and Regions

Description: Code commenting and organization features.

**Single-Line Comments**

**Option 1: Double Slash** (Stored as `//` in Fusion)
```
// This is a comment
int x = 10  // End-of-line comment
```

**Option 2: Single Quote** (User preference, converted to `//`)
```
' This is a comment
int x = 10  ' End-of-line comment
```

**Multi-Line Comments**
```
/* 
 * This is a multi-line comment
 * Spanning multiple lines
 */

/* Quick multi-line comment */
```

**Region Blocks**

Purpose: Collapsible code sections in IDE

```
#Region string_literal_displayed_in_ide
// 0 or more statements
void function processData(Data data)
    // Implementation
    
class Helper
    // Helper class
#End Region

// Example usage
#Region Initialization Code
void function initialize()
    setupSystem()
    loadConfig()
    connectDatabase()
#End Region

#Region Helper Functions
void function helper1()
    // ...

void function helper2()
    // ...
#End Region
```

**Region Features**:
* IDE displays string literal on collapsed region
* Can nest regions
* Helps organize large files
* No effect on compilation

---

### 4. The `...` Operator

Description: Spread/variadic operator for multiple uses.

**Use Case 1: Variadic Functions** (Variable arguments)
```
int function sum(int... numbers)
    int total = 0
    for num in numbers
        total += num
    end loop
    return total

// Usage
int result = sum(1, 2, 3, 4, 5)  // Pass any number of arguments
```

**Use Case 2: Array Spread**
```
int[] numbers1 = [1, 2, 3]
int[] numbers2 = [4, 5, 6]

// Spread into new array
int[] combined = [...numbers1, ...numbers2]  // [1, 2, 3, 4, 5, 6]

// Spread in function call
int result = sum(...combined)
```

**Use Case 3: Range Operator**
```
// Create range
int[] range = [1...10]  // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
int[] range2 = [0...100...10]  // [0, 10, 20, 30, ..., 100] (step 10)

// In for loops
for i in 1...100
    // i goes from 1 to 100
end loop
```

**Use Case 4: Rest Parameters**
```
void function logMessage(string level, string... messages)
    for msg in messages
        print("[{level}] {msg}")
    end loop

// Usage
logMessage("INFO", "Starting", "Loading", "Complete")
```

---

### 5. Enhanced Standard Library

Description: Comprehensive built-in library for common tasks.

---

#### 5.1 File Format Support

**Text Formats**:
* txt - Plain text
* JSON - JavaScript Object Notation
* ini - Configuration files
* xml - Extensible Markup Language
* csv - Comma-Separated Values
* yaml - YAML Ain't Markup Language

**API Design**:
```
// JSON Example
import Fusion.IO.JSON

// Read
JSON json = JSON.parse(fileContent)
string name = json.getString("name")
int age = json.getInt("age")

// Write
JSON output = JSON.create()
output.put("name", "Enterprise")
output.put("speed", 100.0)
string jsonString = output.toString()

// File operations
JSON data, Error err = JSON.readFile("config.json")
if err
    print("Error: {err.message}")

err2 = JSON.writeFile("output.json", data)
```

**CSV Example**:
```
import Fusion.IO.CSV

CSV csv, Error err = CSV.readFile("data.csv")
if not err
    for row in csv.rows
        string name = row.getString(0)
        int value = row.getInt(1)
    end loop
```

---

#### 5.2 Programming Language Support

**Supported Languages**:
* Go, Fusion, Java, C, C++, VB.NET
* JavaScript, HTML, CSS

**Components**:
* **Lexer**: Tokenize source code
* **Parser**: Build Abstract Syntax Tree (AST)
* **Compiler**: Generate executable/bytecode
* **Interpreter**: Execute directly
* **Custom Format Creator**: Define new language syntax

**API Design**:
```
import Fusion.Compiler

// Compile Fusion code
Compiler fusionCompiler = Compiler.create(Language.FUSION)
Program program, Error err = fusionCompiler.compile("source.fusion")
if err
    print("Compilation error: {err.message}")
else
    program.execute()

// Parse Java code
Parser javaParser = Parser.create(Language.JAVA)
AST ast, Error err2 = javaParser.parse(javaCode)

// Lexer example
Lexer lexer = Lexer.create(Language.CPP)
List<Token> tokens = lexer.tokenize(cppCode)
```

---

#### 5.3 Image Format Support

**Supported Formats**:
* BMP - Bitmap
* JPEG/JPG - Joint Photographic Experts Group
* GIF - Graphics Interchange Format
* PNG - Portable Network Graphics

**API Design**:
```
import Fusion.Graphics.Image

// Read image
Image img, Error err = Image.load("photo.jpg")
if not err
    int width = img.width
    int height = img.height
    
    // Edit image
    img.resize(800, 600)
    img.rotate(90)
    img.setPixel(10, 10, Color.RED)
    
    // Save
    err2 = img.save("output.png", ImageFormat.PNG)

// Create new image
Image canvas = Image.create(640, 480, Color.WHITE)
canvas.drawLine(0, 0, 100, 100, Color.BLACK)
canvas.save("drawing.png")
```

---

#### 5.4 Advanced Binary Formats

**Supported Formats**:
* DOC/DOCX - Microsoft Word
* XLS/XLSX - Microsoft Excel
* PDF - Portable Document Format
* ZIP - Compressed archive

**API Design**:
```
import Fusion.Documents

// Read Word document
Document doc, Error err = Document.load("report.docx")
if not err
    string text = doc.getText()
    
    // Edit
    doc.appendText("New paragraph")
    doc.save("modified.docx")

// Excel
import Fusion.Spreadsheet

Workbook wb, Error err = Workbook.load("data.xlsx")
Sheet sheet = wb.getSheet("Sheet1")
string cell = sheet.getCell("A1").getValue()
sheet.setCell("B1", "New Value")
wb.save()

// PDF
import Fusion.PDF

PDF pdf = PDF.create()
pdf.addPage()
pdf.drawText(100, 700, "Hello PDF!")
pdf.save("output.pdf")

// ZIP
import Fusion.Archive

ZIP zip = ZIP.create("archive.zip")
zip.addFile("file1.txt")
zip.addFile("file2.txt")
zip.close()

ZIP existing, Error err = ZIP.open("data.zip")
List<string> files = existing.listFiles()
string content = existing.extractText("readme.txt")
```

---

#### 5.5 Custom Format Creator

Description: Framework for defining new file formats.

```
import Fusion.Format

// Define custom format
FormatDefinition myFormat = FormatDefinition.create("myformat")
myFormat.setMagicBytes([0x4D, 0x59, 0x46, 0x4D])  // "MYFM"
myFormat.defineField("header", FieldType.STRING, 32)
myFormat.defineField("version", FieldType.INT32)
myFormat.defineField("data", FieldType.BYTES, -1)  // Variable length

// Create reader
FormatReader reader = FormatReader.create(myFormat)
CustomData data, Error err = reader.read("file.myformat")

// Create writer
FormatWriter writer = FormatWriter.create(myFormat)
writer.setField("header", "My Custom Format")
writer.setField("version", 1)
writer.setField("data", byteData)
writer.write("output.myformat")
```

---

#### 5.6 Language Localization Support

**Supported Languages**: English, Japanese, Spanish, French, German, Chinese, etc.

**API Design**:
```
import Fusion.Localization

// Set language
Locale.setCurrent("ja-JP")  // Japanese

// Get translated strings
string greeting = Locale.getString("greeting")  // "こんにちは"
string farewell = Locale.getString("farewell")  // "さようなら"

// String files
// en-US.lang
greeting=Hello
farewell=Goodbye

// ja-JP.lang
greeting=こんにちは
farewell=さようなら

// Formatted strings
string message = Locale.format("welcome_user", userName)
```

---

### 6. Loop Enhancements

Description: Compiler automatic protections.

**Automatic Protections**:

```
// User writes simple loop
for i in range(1000)
    processData(i)
end loop

// Compiler automatically adds:
// 1. Infinite loop protection (based on system resources)
// 2. Thread interrupt checking (for graceful shutdown)
// 3. Resource monitoring (RAM/CPU usage)

// User doesn't see this, but compiler generates:
for i in range(1000)
    // [COMPILER INSERTED] Check iteration count
    // [COMPILER INSERTED] Check thread interrupts
    // [COMPILER INSERTED] Monitor system resources
    
    processData(i)
end loop
```

**Settings**:
* Default iteration limit: 1,000,000
* Configurable per project: `fusion.config.max_iterations = 10000000`
* Based on system resources: Adjusts limits based on available RAM/CPU
* Thread interrupt handling: Automatic response to shutdown signals

**User Can Override**:
```
// Disable automatic protection (use with caution!)
#[no_loop_protection]
while true
    // Intentional infinite loop
    processServerRequest()
end loop
```

---

### 7. Array Methods with `?.` Support

Description: Safe navigation for array operations.

```
int[]? numbers = getNumbers()

// Safe array access
int? first = numbers?[0]  // Returns null if array is null
int length = numbers?.length  // Returns 0 if null

// Safe method calls
int? sum = numbers?.sum()
int[]? doubled = numbers?.map(lambda x: x * 2)

// Chaining
int? max = numbers?.filter(lambda x: x > 10)?.max()

// Must handle errors manually
if numbers?.null
    print("Array is null!")
else
    for num in numbers
        print(num)
    end loop
```

**Note**: `?.` is optional. If used, programmer must handle null case manually afterward.

---

### 8. Reserved Words and Operators

Description: Complete list of language keywords.

---

#### Reserved Keywords

**Control Flow**:
* if, elif, else
* match, case
* for, while, do
* break, continue
* return
* end (end loop, end function, etc.)

**Type Declarations**:
* class, struct, interface, enum
* property
* var, const
* static

**Access Modifiers**:
* public, private, protected, internal

**Memory & Pointers**:
* unsafe
* allocate, deallocate
* Unique, Shared, Weak

**Functions & Methods**:
* function
* constructor
* lambda
* async, await

**Modules**:
* module
* import, export

**Operators & Logic**:
* and, or, not
* is, in
* where

**Threading**:
* thread, channel
* goroutine
* lock, unlock
* try (try-with-resources)

**Error Handling**:
* try, catch, finally
* throw, Error

**Literals**:
* true, false
* null, none

**Special**:
* this, super
* goto (reserved but not used, except in unsafe embedded mode)

---

#### Operators

**Arithmetic**:
* `+` Addition
* `-` Subtraction
* `*` Multiplication
* `/` Division
* `%` Modulo
* `**` Exponentiation

**Comparison**:
* `==` Equal
* `!=` Not equal
* `<>` Not equal (alternative)
* `<` Less than
* `>` Greater than
* `<=` Less than or equal
* `>=` Greater than or equal

**Logical**:
* `and` Logical AND
* `or` Logical OR
* `not` Logical NOT
* `&&` Alternative AND
* `||` Alternative OR
* `!` Alternative NOT

**Bitwise**:
* `&` Bitwise AND
* `|` Bitwise OR
* `^` Bitwise XOR
* `~` Bitwise NOT
* `<<` Left shift
* `>>` Right shift

**Assignment**:
* `=` Assignment
* `+=` Add and assign
* `-=` Subtract and assign
* `*=` Multiply and assign
* `/=` Divide and assign
* `%=` Modulo and assign

**Other**:
* `.` Member access
* `?.` Safe navigation
* `??` Null coalescing
* `[]` Array/index access
* `?[]` Safe array access
* `()` Function call / grouping
* `->` (not used, replaced by return-type-first)
* `...` Spread/variadic/range
* `::` Scope resolution (if needed)

---

### 9. Static and Const Clarifications

Description: Class-level members and constants.

**Static Methods**:
```
class MathUtils
    // Static method - belongs to class, not instance
    public static int function max(int a, int b)
        if a > b
            return a
        else
            return b
    
    // Private static
    private static void function internalHelper()
        // Only accessible within class

// Usage - no instance needed
int result = MathUtils.max(10, 20)
```

**Static Fields**:
```
class Counter
    private static int count = 0
    
    constructor()
        Counter.count += 1
    
    public static int function getCount()
        return count

// All instances share same count
Counter c1 = Counter()  // count = 1
Counter c2 = Counter()  // count = 2
int total = Counter.getCount()  // 2
```

**Constants** (Automatically Static):
```
class Config
    // Const is automatically static
    public const string VERSION = "1.0.0"
    private const int MAX_CONNECTIONS = 100
    
    // No need to write "static const"

// Usage
string ver = Config.VERSION  // OK
```

**Rules**:
* Static methods can only access static members
* Instance methods can access both static and instance members
* Static members shared across all instances
* Const is implicitly static (cannot create instance const)
* Static members can be public or private

---

### 10. Weak Pointers - Discouraged

Description: Usage policy for weak pointers.

**Policy**:
* Weak pointers discouraged in normal code
* In strict mode: Compiler error when using Weak<T>
* Only allowed in standard mode with warning
* Better alternative: Redesign object relationships

**Why Discouraged**:
* Adds complexity
* Easy to misuse
* Often indicates design problem
* Most developers don't need them

**When Allowed** (Standard mode only):
```
// Warning: Use of Weak pointer detected
class Node
    Shared<Node> next
    Weak<Node> previous  // Prevent circular reference

// Compiler warning: "Consider redesigning to avoid weak pointers"
```

**Better Alternatives**:
* Use message passing instead
* Redesign object lifetime
* Use events/observers without references
* Single ownership with notifications

---

### 11. Try-With-Resources

Description: Automatic resource locking for thread safety.

**Concept**: Compiler automatically locks resources when accessed by threads.

**Automatic Locking**:
```
class BankAccount
    private float balance
    
    void function withdraw(float amount)
        // Compiler automatically adds:
        // lock(this)
        balance -= amount
        // unlock(this)

// When multiple threads call withdraw:
thread1: account.withdraw(100)  // Locked
thread2: account.withdraw(50)   // Waits for lock
// No race condition!
```

**Manual Control**:
```
BankAccount account = BankAccount()

// Explicit lock scope
try (account)
    // Lock acquired automatically
    account.withdraw(100)
    account.deposit(50)
    // Lock released automatically at end of block

// Lock automatically released even if exception occurs
```

**File Handling**:
```
// Automatic file locking
try (file = File.open("data.txt", FileMode.READ_WRITE))
    string content = file.readAll()
    file.write("New content")
    // File automatically closed and lock released

// No explicit close() needed!
```

**Multiple Resources**:
```
try (file1 = File.open("input.txt"), file2 = File.open("output.txt"))
    string data = file1.readAll()
    file2.write(data)
    // Both files auto-closed in reverse order
```

**Benefits**:
* Prevents resource leaks
* Automatic lock management
* Prevents deadlocks (compiler orders locks)
* Exception-safe
* Less boilerplate code

---

### 12. Template Notation Clarification

Description: Proper notation for language templates.

**Notation Rules**:

Symbol | Meaning | Example
---|---|---
`<>` | Placeholder for type or name | `<returnType>`, `<name>`
`{}` | Optional element | `{= defaultValue}`
`[]` | Array/List brackets | `int[]`, `List<int>`
`...` | Variable arguments | `int... numbers`

**Template Format**:
```
// Full function template
<returnType> function <name>(<type> <param> {= <defaultValue>}, ...)

// Expanded:
// <returnType> - Any valid type (int, string, MyClass, etc.)
// <name> - Function name (identifier)
// <type> - Parameter type
// <param> - Parameter name
// {= <defaultValue>} - Optional default value

// Real examples:
int function add(int a, int b)
void function print(string message = "Hello")
Spaceship function create(string name, float speed = 100.0)
```

**Block Syntax Template**:
```
<returnType> function <name>(<params>) {
    <statements>
}

// Or indentation:
<returnType> function <name>(<params>)
    <statements>

// {} means braces are optional (user preference)
```

**Loop Template**:
```
while <condition>
    <statements>
end loop {with <options>}

// {} around "with" means it's optional
// <options> is placeholder for check specifications
```

---

## Implementation Priority

Description: Order of additions.

**Phase 1: Critical Features** (Do First):
1. Enums
2. Comparison operators (`<>`)
3. Comments and regions
4. Reserved words and operators list
5. Static and const clarifications
6. Template notation

**Phase 2: Standard Library** (Do Second):
1. File format support (JSON, XML, CSV, etc.)
2. Text file readers/writers
3. Image format support
4. Basic localization

**Phase 3: Advanced Features** (Do Third):
1. Programming language support (compilers/parsers)
2. Advanced binary formats (DOC, PDF, ZIP)
3. Custom format creator
4. Full localization system

**Phase 4: Documentation** (Do Last):
1. Update all existing documents
2. Add examples for each feature
3. Create API reference
4. Write tutorials

---

## Files to Update

Description: Which files need modifications.

**1. fusion-language-spec.md**:
* Add Enums section
* Add `<>` to comparison operators
* Add comments and regions section
* Update reserved words and operators
* Add `...` operator usage
* Clarify static and const
* Add try-with-resources details
* Add automatic loop protection notes
* Update standard library section

**2. fusion-templates.md**:
* Add enum templates
* Clarify template notation
* Add `...` operator templates
* Add try-with-resources template
* Add region template

**3. fusion-threading-concurrency.md**:
* Add try-with-resources section
* Add compiler lock insertion details
* Add thread section analysis explanation
* Add IDE visualization details

**4. Create: fusion-standard-library.md**:
* Complete API reference
* File formats
* Image processing
* Language support
* Localization
* Custom format framework

---

## Next Steps

Description: Await approval before proceeding.

**User Review Required**:
1. Enum syntax preference (braces, indentation, or single-line)
2. Approval of standard library design
3. Confirmation of all reserved words
4. Verification of operator set
5. Approval of template notation

**Upon Approval**:
1. Update fusion-language-spec.md
2. Update fusion-templates.md
3. Update fusion-threading-concurrency.md
4. Create fusion-standard-library.md
5. Update fusion-summary.md

---

## Questions for User

Description: Need decisions on these items.

**Question 1**: Which enum syntax do you prefer?
* Option A: `Enum Name { ... }`
* Option B: `Enum Name` with indentation
* Option C: `Enum Name: VALUE1, VALUE2`
* Or support all three?

**Question 2**: For `...` operator, which uses should we support?
* Variadic functions: Yes/No?
* Array spread: Yes/No?
* Range operator: Yes/No?
* Rest parameters: Yes/No?

**Question 3**: Comment preference
* Support both `//` and `'` for single-line?
* Or standardize on one?

**Question 4**: Standard library priority
* Which file formats are most important?
* Which language support is most important?

---

## Summary

**Total New Features**: 12 major additions
**Files to Update**: 3 existing documents
**Files to Create**: 1 new document (standard library)
**Estimated Scope**: Large update covering syntax, standard library, and tooling

**Ready for Approval**: All features documented and explained. Awaiting user confirmation before implementation.
