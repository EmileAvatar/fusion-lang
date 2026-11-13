[< 035 HIDL](035-HIDL.md) | [Index](index.md) | [050 Imports >](050-Imports.md) <!-- nav -->

# 040 Cross Language

**Status:** planned - the language modules `Lang.<language>.<optional flavour>.Fusion` are FEATURES Task 49 (after self-hosting, Task 35; D.105, D.121, D.137)

## Cross-Language Compilation Support

**Superseded in part (user, 2026-11-03):** the design is now
`files/Fusion_Multi_Language_Compiler_Architecture.md` - `Lang.<language>.Fusion` modules
through one injection point, a Migration IR, new .fusion files; after self-hosting (files/FEATURES.md
Task 49, D.105). Semicolons and the parser notes below still stand (SYN.037).

**Status:** 📝 Proposed (Post-MVP)
**Priority:** Medium (after working compiler is complete)
**Purpose:** Enable Fusion to compile and interoperate with code from other languages

### Overview

- Fusion aims to support compilation of multiple programming languages through its `fusionlib.Lang` module.
- To achieve this, the Fusion parser needs to support various syntax conventions used by different languages.

### Semicolon Support

**Current State:** Fusion lexer does **not** tokenize semicolons (`;`). Statements are terminated by newlines or block boundaries.

**Proposed Enhancement:**
- Add semicolon tokenization to the lexer
- Make semicolons optional statement terminators (like Swift, JavaScript, Kotlin)
- Support both styles: newline-terminated AND semicolon-terminated statements
- Enable parsing of C/C++/Java-style code with semicolons

**Rationale:**
To compile C, C++, Java, C#, and other semicolon-based languages through `fusionlib.Lang`, the Fusion parser must understand semicolon syntax.

**Example:**
```fusion
// Current Fusion (newline-terminated)
int x = 5
int y = 10
return x + y

// Future Fusion (semicolon-terminated - optional)
int x = 5;
int y = 10;
return x + y;

// Mixed (both valid)
int x = 5;
int y = 10
return x + y;
```

### Cross-Language Parsing Support

**Languages to Support via fusionlib.Lang:**
1. **C** - Semicolons, preprocessor directives, pointer syntax
2. **C++** - Templates, namespaces, operator overloading
3. **Java** - Packages, interfaces, annotations
4. **C#** - Properties, LINQ, async/await
5. **Python** - Indentation-based (already supported), decorators
6. **JavaScript** - Prototypes, arrow functions, optional semicolons
7. **TypeScript** - Type annotations, interfaces
8. **Go** - Implicit semicolons, goroutines
9. **Rust** - Macros, lifetimes, ownership syntax
10. **VB.NET** - End keyword syntax (already supported)

### Implementation Strategy

**Phase 1: Lexer Enhancement**
- Add `TokenType.SEMICOLON` to token definitions
- Update lexer to recognize `;` as a delimiter
- Make semicolons optional (don't require them)

**Phase 2: Parser Enhancement**
- Update `consume_statement_terminator()` to accept semicolons OR newlines
- Ensure backward compatibility (existing Fusion code still works)
- Add tests for semicolon-terminated statements

**Phase 3: Language-Specific Parsers**
- Create specialized parsers for each target language
- Implement in `fusionlib.Lang` module
- Convert foreign language AST → Fusion AST → C code

**Phase 4: Syntax Extension System**
- Plugin architecture for custom syntax
- Allow community-contributed language parsers
- Standard API for AST conversion

### Benefits

1. **Multi-language compilation** - Compile any language through Fusion
2. **Developer flexibility** - Use semicolons or not, developer's choice
3. **IDE support** - Better interoperability with existing tools
4. **Migration path** - Easier to migrate C/Java code to Fusion
5. **Ecosystem growth** - Support for more languages = larger community

### Timeline

- **Phase 1 (Semicolon Support):** 1-2 weeks (after MVP compiler complete)
- **Phase 2 (Parser Updates):** 1 week
- **Phase 3 (Language Parsers):** 6-12 months (incremental per language)
- **Phase 4 (Plugin System):** 2-3 months

### Dependencies

- ✅ Basic compiler must be complete (Milestone 4)
- ✅ Parser must be fully functional
- ⚪ fusionlib.Lang module must be implemented
- ⚪ AST must be stable and well-documented

### Success Criteria

- [ ] Fusion code works with or without semicolons
- [ ] Can parse valid C code and compile to executable
- [ ] Can parse valid Java code and compile to executable
- [ ] Can parse valid Python code and compile to executable
- [ ] Backward compatibility: All existing Fusion code still works
- [ ] Comprehensive test suite for each supported language
- [ ] Documentation for cross-language compilation

### Notes

- This feature is **not part of MVP** - implement after basic compiler works
- Semicolons remain **optional** in Fusion - they're for compatibility
- Fusion's native style (newline-terminated) is still recommended
- Cross-language support enables Fusion to become a universal compiler frontend

---


## Future Self-Hosting Considerations

When the compiler is rewritten in Fusion (self-hosting), these modules become critical:

**Why fusionlib.IDE matters for self-hosting:**
1. Compiler developers need IDE support to write compiler in Fusion
2. Language Server needed for auto-completion while coding compiler
3. Syntax highlighting makes compiler code easier to read
4. Formatter helps maintain consistent code style

**Why Settings matter for self-hosting:**
1. Compiler needs to read its own build configuration
2. CompilerSettings used internally by compiler
3. Self-compilation requires understanding target platform

[< 035 HIDL](035-HIDL.md) | [Index](index.md) | [050 Imports >](050-Imports.md) <!-- nav -->
