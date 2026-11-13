[< 060 Comments](060-Comments.md) | [Index](index.md) <!-- nav -->

# 061 Comment Highlighting

**Status:** idea - no task (with SYN.036)

## Feature 2a: Language-Specific Syntax Highlighting in `'''` Blocks

**Status:** 📝 Proposed (Post-Compiler)
**Priority:** Low (IDE enhancement)
**Depends On:** Working compiler + IDE module + Language Server Protocol (LSP)

**Purpose:** Allow `'''` comment blocks to specify a language for syntax highlighting in IDEs and documentation viewers.

**Syntax:**
```fusion
'''language_name
code or text here with syntax highlighting
'''
```

**Supported Languages:**
- `fusion` - Fusion language syntax
- `python` - Python syntax
- `javascript` / `js` - JavaScript syntax
- `typescript` / `ts` - TypeScript syntax
- `csharp` / `cs` - C# syntax
- `java` - Java syntax
- `cpp` / `c++` - C++ syntax
- `c` - C syntax
- `rust` - Rust syntax
- `go` - Go syntax
- `sql` - SQL syntax
- `json` - JSON syntax
- `xml` - XML syntax
- `html` - HTML syntax
- `css` - CSS syntax
- `bash` / `shell` - Shell script syntax
- `markdown` / `md` - Markdown syntax
- And any other language supported by the IDE's syntax highlighter

**Examples:**

**Example 1: Fusion Code in Comments**
```fusion
'''fusion
// Example of Fusion code in documentation
int function add(int a, int b)
    return a + b
'''

int function multiply(int a, int b)
    '''fusion
    This could also be written as:
    int multiply(int a, int b) : a * b
    '''
    return a * b
```

**Example 2: Python Comparison**
```fusion
'''
This Fusion function is equivalent to the following Python code:
'''

'''python
def add(a, b):
    return a + b
'''

int function add(int a, int b)
    return a + b
```

**Example 3: SQL in Documentation**
```fusion
class UserRepository
    '''
    Executes the following SQL query:
    '''

    '''sql
    SELECT id, name, email
    FROM users
    WHERE active = 1
    ORDER BY name
    '''

    List<User> function getActiveUsers()
        // Implementation here
```

**Example 4: JSON Configuration Example**
```fusion
'''
Configuration file format (config.json):
'''

'''json
{
    "app": {
        "name": "MyApp",
        "version": "1.0.0",
        "debug": true
    }
}
'''
```

**Grammar:**
```ebnf
triple_quote_comment = "'''" [language_identifier] { character | newline } "'''"

language_identifier = letter { letter | digit | "_" | "-" }
  (* Optional language name on same line as opening ''' *)
```

**Parsing Rules:**
1. If `'''` is followed by text on the same line → treat as language identifier
2. Language identifier must be alphanumeric + `_` + `-` (no spaces)
3. Language identifier ends at newline
4. If no language specified → plain comment (no syntax highlighting)
5. Unknown language names → treat as plain comment (no error)

**IDE Integration:**

**For IDEs (VS Code, IntelliJ, Sublime, Vim):**
- Parse `'''language` directive
- Apply syntax highlighting for specified language within comment block
- Show in documentation preview with proper formatting
- Language Server Protocol (LSP) provides language hints

**For Documentation Generators (fusionlib.DocWiki):**
- Convert `'''language` blocks to properly formatted code blocks
- Generate syntax-highlighted HTML/Markdown
- Support light/dark themes

**Implementation Notes:**

**Lexer Changes:**
```python
# In src/lexer/comments.py

def skip_triple_quote_comment(text: str, position: int) -> Tuple[int, int, Optional[str]]:
    """Skip a triple-quote comment block with optional language hint.

    Returns:
        Tuple of (new_position, lines_consumed, language_hint)
        language_hint is None if no language specified
    """
    pos = position

    # Must start with '''
    if pos + 2 >= len(text) or text[pos:pos + 3] != "'''":
        return position, 0, None

    pos += 3  # Skip '''

    # Check for language identifier on same line
    language_hint = None
    line_start = pos
    while pos < len(text) and text[pos] not in ['\n', '\r']:
        pos += 1

    lang_text = text[line_start:pos].strip()
    if lang_text and lang_text.replace('_', '').replace('-', '').isalnum():
        language_hint = lang_text.lower()

    # Continue to closing '''
    # ... (rest of implementation)

    return new_pos, lines_consumed, language_hint
```

**Token Changes:**
```python
# In src/lexer/token.py

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    location: SourceLocation
    language_hint: Optional[str] = None  # For '''language blocks
```

**LSP (Language Server Protocol) Integration:**
- Provide `textDocument/semanticTokens` with language hints
- IDEs query LSP for syntax highlighting within `'''language` blocks
- LSP returns token ranges with language identifiers

**Use Cases:**

1. **Code Examples in Documentation**
   - Show equivalent code in other languages
   - Compare Fusion syntax to Python/C#/Java/etc.

2. **Configuration Examples**
   - Document JSON/YAML/XML config file formats
   - Show SQL queries in database modules

3. **Cross-Language Interop Documentation**
   - Show C/C++ FFI examples
   - Document external API calls (REST, GraphQL)

4. **Teaching and Tutorials**
   - Side-by-side comparisons of languages
   - Educational comments with highlighted examples

5. **Code Migration Notes**
   - Document original code from other languages
   - Show translation notes during porting

**Edge Cases:**

```fusion
''' This is NOT a language hint (has space after ''')
No syntax highlighting
'''

'''python This is NOT valid (space in identifier)
No syntax highlighting
'''

'''python-3.11 This IS valid (hyphen allowed)
Syntax highlighting as Python
'''

'''c++ This IS valid
Syntax highlighting as C++
'''

'''UnknownLang This is valid but unknown language
No syntax highlighting (treated as plain comment)
'''

''''fusion This is 4 quotes - ERROR (see note below)
''''
```

**Note on `''''` (Four Quotes):**
This syntax (`''''`) is **NOT** supported. The lexer would interpret this as:
1. `'''` → Start of comment block
2. `'` → Part of comment content
3. Must close with `'''`

To avoid confusion:
- Lexer only recognizes exactly `'''` (three quotes)
- `''''` is invalid and would cause unterminated comment error
- Users should only use `'''` (three quotes)

**Timeline:**
- **Phase 1:** Basic `'''` comments (2-4 days) - Part of Enhanced Comment Support
- **Phase 2:** Language hint parsing (1 day) - Lexer modification
- **Phase 3:** IDE integration via LSP (3-5 days) - Requires fusionlib.IDE module
- **Phase 4:** DocWiki integration (2-3 days) - Documentation generation

**Total:** 8-13 days (AFTER compiler MVP complete)

**Benefits:**

**For Documentation:**
- ✅ Rich code examples with syntax highlighting
- ✅ Multi-language comparison in single file
- ✅ Better generated documentation (HTML/PDF)

**For Developers:**
- ✅ Easier to read embedded code examples
- ✅ IDE provides syntax checking for examples
- ✅ Copy-paste code examples stay formatted

**For Teaching:**
- ✅ Language comparison tutorials
- ✅ Migration guides with side-by-side code
- ✅ Interactive learning materials

[< 060 Comments](060-Comments.md) | [Index](index.md) <!-- nav -->
