# Built-in functions and methods

**Generated from the compiler** by `python check.py --builtins` (Task 28.1.4) - do not edit by hand.
`python check.py` fails when this file no longer matches the compiler.

96 functions, 15 List methods, 7 Map methods. Examples of each are in `SYNTAX_REFERENCE.md`.

- **Layer:** the lowest `[stdlib] layer` that allows it - `core` (no heap), `alloc` (no operating system), `std` (everything)
- **Fails:** it can raise an error (catch it with `try`, or capture it); any function that makes text can also fail with StringTooLongError when `[strings] max_length` is set
- **Methods:** a function can also be called as a method on its first argument - `name.trim()` is `trim(name)` - and through its type class - `String.trim(name)` (not `format`, `print`, `range`, `write`)

#### Program, output and input

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `print(string text, any...)` | `void` | std |  |
| `write(string text, any...)` | `void` | std |  |
| `format(string text, any...)` | `string` | alloc |  |
| `exit(int)` | `void` | std |  |
| `readLine()` | `string` | std |  |
| `isEndOfInput()` | `bool` | std |  |
| `run(string)` | `int` | std | yes |

#### Files

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `readText(string)` | `string` | std | yes |
| `readLines(string)` | `List<string>` | std | yes |
| `writeText(string, string)` | `void` | std | yes |
| `appendText(string, string)` | `void` | std | yes |
| `readBytes(string)` | `bytes` | std | yes |
| `writeBytes(string, bytes)` | `void` | std | yes |
| `fileExists(string)` | `bool` | std |  |
| `deleteFile(string)` | `void` | std | yes |

#### Core

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `len(string \| array \| bytes)` | `int` | core |  |
| `range(int from, int to, int step = 1)` | `the numbers, for a loop` | core |  |
| `charCode(char)` | `int` | core |  |
| `fromCharCode(int)` | `char` | core | yes |
| `toByte(int)` | `byte` | core | yes |
| `wrapAdd(int, int)` | `int` | core |  |
| `wrapSub(int, int)` | `int` | core |  |
| `wrapMul(int, int)` | `int` | core |  |

#### Text - inspect and search

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `isEmpty(string)` | `bool` | alloc |  |
| `isBlank(string)` | `bool` | alloc |  |
| `isDigits(string)` | `bool` | alloc |  |
| `isLetters(string)` | `bool` | alloc |  |
| `isAscii(string)` | `bool` | alloc |  |
| `isInt(string, int = 10)` | `bool` | alloc | yes |
| `isFloat(string)` | `bool` | alloc |  |
| `contains(string, string)` | `bool` | alloc |  |
| `containsAny(string, string)` | `bool` | alloc |  |
| `startsWith(string, string)` | `bool` | alloc |  |
| `endsWith(string, string)` | `bool` | alloc |  |
| `indexOf(string, string, int = 0)` | `int` | alloc |  |
| `lastIndexOf(string, string)` | `int` | alloc |  |
| `countOf(string, string)` | `int` | alloc |  |
| `lenb(string)` | `int` | alloc |  |

#### Text - compare

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `equalsIgnoreCase(string, string)` | `bool` | alloc |  |
| `compareIgnoreCase(string, string)` | `int` | alloc |  |
| `compareNatural(string, string, bool = false)` | `int` | alloc |  |

#### Text - extract and change

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `substring(string, int, int)` | `string` | alloc | yes |
| `left(string, int)` | `string` | alloc | yes |
| `right(string, int)` | `string` | alloc | yes |
| `insert(string, int, string)` | `string` | alloc | yes |
| `remove(string, int, int)` | `string` | alloc | yes |
| `replace(string, string, string)` | `string` | alloc | yes |
| `replaceFirst(string, string, string)` | `string` | alloc | yes |
| `repeat(string, int)` | `string` | alloc | yes |
| `reverse(string)` | `string` | alloc |  |
| `truncate(string, int)` | `string` | alloc | yes |
| `trim(string)` | `string` | alloc |  |
| `trimStart(string)` | `string` | alloc |  |
| `trimEnd(string)` | `string` | alloc |  |
| `toUpper(string)` | `string` | alloc |  |
| `toLower(string)` | `string` | alloc |  |
| `capitalize(string)` | `string` | alloc |  |
| `toTitle(string)` | `string` | alloc |  |
| `padLeft(string, int, char = ' ')` | `string` | alloc | yes |
| `padRight(string, int, char = ' ')` | `string` | alloc | yes |
| `center(string, int, char = ' ')` | `string` | alloc | yes |
| `asciiOnly(string, char)` | `string` | alloc |  |
| `digitsOnly(string)` | `string` | alloc |  |

#### Text - split and join

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `split(string, string)` | `List<string>` | alloc |  |
| `join(List<string>, string)` | `string` | alloc | yes |
| `lines(string)` | `List<string>` | alloc |  |
| `words(string)` | `List<string>` | alloc |  |

#### Text - masks

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `mask(string, int, int, char = '*')` | `string` | alloc | yes |
| `maskEmail(string, int = 1, char = '*')` | `string` | alloc | yes |
| `formatMask(string, string)` | `string` | alloc |  |

#### Conversions and formatting

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `toString(int \| float \| double \| bool \| char \| byte \| bytes)` | `string` | alloc |  |
| `toInt(string)` | `int` | alloc | yes |
| `toFloat(string)` | `float` | alloc | yes |
| `parseInt(string, int)` | `int` | alloc | yes |
| `formatNumber(double, string)` | `string` | alloc | yes |

#### Number bases

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `toHex(int \| string, int = 0)` | `string` | alloc | yes |
| `toBinary(int \| string, int = 0)` | `string` | alloc | yes |
| `toOctal(int \| string, int = 0)` | `string` | alloc | yes |
| `toBase(int \| string, int, int = 0)` | `string` | alloc | yes |
| `fromHex(string)` | `int` | alloc | yes |
| `fromBinary(string)` | `int` | alloc | yes |
| `fromOctal(string)` | `int` | alloc | yes |

#### Raw bytes

| Function | Returns | Layer | Fails |
|---|---|---|---|
| `toBytes(string \| char \| int \| byte, bool = false)` | `bytes` | alloc |  |
| `newBytes(int, byte = 0)` | `bytes` | alloc | yes |
| `byteAt(string, int)` | `int` | alloc | yes |
| `getInt(bytes, int, bool = false)` | `int` | alloc | yes |
| `getInt16(bytes, int, bool = false)` | `int` | alloc | yes |
| `getUInt16(bytes, int, bool = false)` | `int` | alloc | yes |
| `setInt(bytes, int, int, bool = false)` | `void` | alloc | yes |
| `setInt16(bytes, int, int, bool = false)` | `void` | alloc | yes |
| `slice(bytes, int, int)` | `bytes` | alloc | yes |
| `isText(bytes)` | `bool` | alloc |  |
| `rawToHex(bytes)` | `string` | alloc | yes |
| `hexToRaw(string)` | `bytes` | alloc | yes |
| `bytesToHex(string)` | `string` | alloc | yes |
| `hexToBytes(string)` | `string` | alloc | yes |

#### Type classes

Each built-in type has a class holding its functions as methods (Task 18.3.7):

| Class | Type | Also (not taking the type first) |
|---|---|---|
| `String` | `string` |  |
| `Bytes` | `bytes` | `Bytes.hexToRaw`, `Bytes.newBytes`, `Bytes.toBytes` |
| `Int` | `int` | `Int.fromBinary`, `Int.fromHex`, `Int.fromOctal`, `Int.parseInt` |
| `Char` | `char` | `Char.fromCharCode` |
| `Float` | `float` |  |
| `Double` | `double` |  |
| `Byte` | `byte` |  |
| `Bool` | `bool` |  |

#### List<T> methods

| Method | Returns | Fails | What it does |
|---|---|---|---|
| `.add(T x)` | `void` |  | add at the end |
| `.insert(int at, T x)` | `void` | yes | insert before position at (IndexError) |
| `.removeAt(int at)` | `void` | yes | remove the element at a position (IndexError) |
| `.remove(T x)` | `bool` |  | remove the first element equal to x; false if none |
| `.clear()` | `void` |  | remove every element |
| `.len()` | `int` |  | the number of elements |
| `.contains(T x)` | `bool` |  | whether an element equals x |
| `.indexOf(T x)` | `int` |  | the first position of x, or -1 |
| `.join(string separator)` | `string` |  | List<string> only: the elements joined |
| `.slice(int start, int count)` | `List<T>` | yes | a copy of count elements from start (IndexError) |
| `.sort()` | `void` |  | sort in place (numbers, chars, text, bools) |
| `.sortBy((T, T) : int compare)` | `void` |  | sort in place by a function |
| `.filter((T) : bool keep)` | `List<T>` |  | the elements the function keeps |
| `.map((T) : U f)` | `List<U>` |  | the function applied to each element |
| `.reduce(U start, (U, T) : U f)` | `U` |  | combine every element into one value |

#### Map<K, V> methods

| Method | Returns | Fails | What it does |
|---|---|---|---|
| `.has(K key)` | `bool` |  | whether the key is there |
| `.get(K key, V default)` | `V` |  | the value, or the default when the key is missing |
| `.remove(K key)` | `bool` |  | remove the key; false if it was not there |
| `.keys()` | `List<K>` |  | the keys, in the order they were added |
| `.values()` | `List<V>` |  | the values, in the same order |
| `.len()` | `int` |  | the number of keys |
| `.clear()` | `void` |  | remove every key |
