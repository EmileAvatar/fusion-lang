[< 170 Build](170-Build.md) | [Index](index.md) | [181 fusionlib-Core >](181-fusionlib-Core.md) <!-- nav -->

# 180 Standard Library

**Contents**

- [Core Collections](#core-collections)
- [Math Library](#math-library)
- [File I/O](#file-io)
- [Text File Formats](#text-file-formats)
- [Programming Language Support](#programming-language-support)
- [Image Formats](#image-formats)
- [Advanced Binary Formats](#advanced-binary-formats)
- [More library areas (moved from the Auto-Documentation section)](#more-library-areas-moved-from-the-auto-documentation-section)
- [Custom Format Creator](#custom-format-creator)
- [Localization Support](#localization-support)
- [Networking](#networking)
- [Graphics and Audio](#graphics-and-audio)
- [Threading and Concurrency](#threading-and-concurrency)
- [Date and Time](#date-and-time)
- [Regular Expressions](#regular-expressions)

## Standard Library

**Status:** [PARTLY] strings, bytes, collections, files and console are built (18.3, 18.5), and
`run(command)` runs another program (28.1.1); the library modules are designed one at a time in Task 43
(fusionlib: [181](181-fusionlib-Core.md), [182](182-fusionlib-Extended.md)). Every built-in function and
method, generated from the compiler: `files/Builtins.md`. Fusion's own libraries live in the `Fusion`
namespace - `Fusion.IO`, `Fusion.Graphics` (D.136, Task 57)

Description: Comprehensive built-in library for common tasks and formats.

---

### Core Collections

* **List<T>**: Dynamic array with resizing - built ([140 Collections](140-Collections.md))
* **Map<K,V>** (also written `Dictionary<K,V>`): Hash map for key-value pairs - built
* **Set<T>**: Unique elements collection
* **Queue<T>**: FIFO queue
* **Stack<T>**: LIFO stack
* Set, Queue, Stack and more (a RingBuffer first): Task 43.4 / 43.5

---

### Math Library

* **Vector**: 2D, 3D, 4D vector operations
* **Matrix**: Matrix operations and transformations
* **Quaternion**: Rotation calculations
* **Math functions**: sin, cos, tan, sqrt, abs, pow, etc.

---

### File I/O

* **Synchronous**: Read/write operations that block
* **Asynchronous**: Non-blocking I/O with async/await ([100 Concurrency](100-Concurrency.md) 4.8)
* Files are services by default (D.072); a file handle manager (43.7)
* **Streams**: Buffered reading and writing

---

### Text File Formats

Description: Built-in support for common text formats - the data formats module (43.2).

**Supported Formats**:
* **txt** - Plain text files
* **md** - Markdown documentation
* **JSON** - JavaScript Object Notation
* **XML** - Extensible Markup Language
* **CSV** - Comma-Separated Values
* **YAML** - YAML Ain't Markup Language
* **ini** - Configuration files

**API Example**:
```
import Fusion.IO.JSON

// Read and parse JSON
JSON data, Error err = JSON.readFile("config.json")
if not err
    string name = data.getString("name")
    int value = data.getInt("value")

// Write JSON
JSON output = JSON.create()
output.put("name", "Spaceship")
output.put("speed", 100.0)
err = JSON.writeFile("output.json", output)
```

**Features**:
* Format-specific reader/writer
* Format validation
* Custom format creator framework

---

### Programming Language Support

Description: Built-in compilers, parsers, and lexers for multiple languages - now the language
modules, `import Lang.Python.Fusion` (D.121, Task 49), after self-hosting.

**Supported Languages**:
* Go, Fusion, Java, C, C++
* VB.NET, JavaScript, HTML, CSS

**Components**:
* **Lexer**: Tokenize source code
* **Parser**: Build Abstract Syntax Tree (AST)
* **Compiler**: Generate executable/bytecode
* **Interpreter**: Execute code directly
* **Custom Language Creator**: Define new language syntax

**API Example**:
```
import Fusion.Compiler

// Compile Fusion code
Compiler fusionCompiler = Compiler.create(Language.FUSION)
Program program, Error err = fusionCompiler.compile("source.fusion")
if not err
    program.execute()

// Parse Java code to AST
Parser javaParser = Parser.create(Language.JAVA)
AST ast, Error err = javaParser.parse(javaCode)
```

---

### Image Formats

Description: Read, write, and manipulate common image formats.

**Supported Formats**:
* BMP - Bitmap
* JPEG/JPG - Joint Photographic Experts Group
* GIF - Graphics Interchange Format
* PNG - Portable Network Graphics

**API Example**:
```
import Fusion.Graphics.Image

// Load image
Image img, Error err = Image.load("photo.jpg")
if not err
    // Edit image
    img.resize(800, 600)
    img.rotate(90)
    img.setPixel(10, 10, Color.RED)
    
    // Save in different format
    err = img.save("output.png", ImageFormat.PNG)
```

**Features**:
* Pixel-level access
* Image transformations
* Format conversion
* Custom format support

---

### Advanced Binary Formats

user added note: eg fusionlib.Data.Zip or fusionlib.Data.PDF or fusionlib.Data.Docx
Description: Support for complex document and archive formats (see fusionlib.Data module).

**Supported Formats**:
* **DOC/DOCX** - Microsoft Word
* **XLS/XLSX** - Microsoft Excel
* **PDF** - Portable Document Format
* **ZIP** - Compressed archives

---

### More library areas (moved from the Auto-Documentation section)

**Word Documents**:
```
import Fusion.Documents

Document doc, Error err = Document.load("report.docx")
if not err
    string text = doc.getText()
    doc.appendText("New content")
    doc.save("modified.docx")
```

**Excel Spreadsheets**:
```
import Fusion.Spreadsheet

Workbook wb, Error err = Workbook.load("data.xlsx")
Sheet sheet = wb.getSheet("Sheet1")
string value = sheet.getCell("A1").getValue()
sheet.setCell("B1", "New Value")
wb.save()
```

**PDF Documents**:
```
import Fusion.PDF

PDF pdf = PDF.create()
pdf.addPage()
pdf.drawText(100, 700, "Hello PDF!")
pdf.save("output.pdf")
```

**ZIP Archives**:
```
import Fusion.Archive

ZIP zip = ZIP.create("archive.zip")
zip.addFile("file1.txt")
zip.addFile("file2.txt")
zip.close()
```

---

### Custom Format Creator

Description: Framework for defining new file formats.

```
import Fusion.Format

// Define custom format
FormatDefinition myFormat = FormatDefinition.create("myformat")
myFormat.setMagicBytes([0x4D, 0x59, 0x46, 0x4D])
myFormat.defineField("header", FieldType.STRING, 32)
myFormat.defineField("version", FieldType.INT32)

// Create reader/writer
FormatReader reader = FormatReader.create(myFormat)
FormatWriter writer = FormatWriter.create(myFormat)
```

---

### Localization Support

Description: Multi-language application support.

**Supported Languages**: English, Japanese, Spanish, French, German, Chinese, and more

**API Example**:
```
import Fusion.Localization

// Set current language
Locale.setCurrent("ja-JP")

// Get translated strings
string greeting = Locale.getString("greeting")  // "こんにちは"

// Formatted strings
string message = Locale.format("welcome_user", userName)
```

---

### Networking

* **HTTP**: Client and server implementations
* **WebSocket**: Real-time bidirectional communication
* **TCP/UDP**: Low-level socket programming

---

### Graphics and Audio

* **2D Graphics**: Drawing primitives, sprites, textures
* **3D Graphics**: Rendering, lighting, shaders
* **Audio**: Sound playback, synthesis, effects

---

### Threading and Concurrency

The design: [100 Concurrency](100-Concurrency.md) - services first; the items below for the other models.

* **Task Parallel Library**: High-level task management
* **Thread Pools**: Efficient worker thread management
* **Channels**: Message passing between threads
* **Async/Await**: Simplified asynchronous programming

---

### Date and Time

The Time module: Task 43.1.

* **DateTime**: Date and time manipulation
* **TimeSpan**: Duration calculations
* **Calendar**: Calendar-specific operations
* **Time zones**: Timezone conversions

---

### Regular Expressions

* **Pattern matching**: Powerful text search and replace
* **Validation**: Input validation with regex
* **Parsing**: Extract data from text

[< 170 Build](170-Build.md) | [Index](index.md) | [181 fusionlib-Core >](181-fusionlib-Core.md) <!-- nav -->
