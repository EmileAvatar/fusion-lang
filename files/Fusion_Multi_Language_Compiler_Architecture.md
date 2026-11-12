# Fusion Multi-Language Compiler Architecture

## High-Level Design Proposal

## 1. High-Level Summary

Fusion should be designed as a **multi-language compiler platform with
Fusion as its primary target language and execution environment**.

The core Fusion compiler should not need to understand the grammar and
special rules of every programming language directly. Instead, it should
provide an **injection point for language modules**. Each language
module supplies the components required to understand, parse, analyse,
translate and, where supported, compile that language.

Examples:

-   `Lang.C.Fusion` -- C language support.
-   `Lang.CPP.Fusion` -- C++ language support.
-   `Lang.Java.Fusion` -- Java language support.
-   `Lang.Python.Fusion` -- Python language support.
-   `Lang.Fusion.Fusion` -- native Fusion language support.

A flavour or version, when a language has several (user, 2026-11-12 - D.137):
`Lang.<language>.<optional flavour>.Fusion` - `Lang.Python.2.Fusion`, `Lang.Python.3.Fusion`.

A language module is more than a syntax definition. It is a
self-contained language package that describes the language's grammar,
tokens, parser behaviour, AST structure, type and semantic rules,
compilation requirements, and translation rules.

The compiler loads the selected language module through its language
injection interface. The module reads the source code and produces that
language's AST. The compiler can then pass the AST to the module's
semantic and translation components.

For migration, the language module can convert its source AST into
Fusion's AST. Fusion's normal code generator then produces new `.fusion`
source files. The original source files are never modified.

The intended architecture is:

``` text
                  Fusion Compiler
                         |
             Language Injection Interface
                         |
              Loads Lang.<language>.Fusion
                         |
             Language-specific front end
                         |
       Source → Tokens → Parser → Source AST
                         |
             Language semantic analysis
                         |
               Language translation rules
                         |
                  Migration IR
                         |
                  Fusion AST
                         |
             Fusion semantic validation
                         |
              Fusion code generator
                         |
                 New .fusion files
```

The same language module should also be able to provide the components
needed to compile that language according to its own rules, where the
required runtime, ABI, libraries and target backend are available.

This gives Fusion two related capabilities:

1.  **Native language compilation:** understand and compile a source
    language according to that language's rules.
2.  **Language migration:** understand the source language, translate
    its meaning into Fusion, and generate new Fusion source code.

Fusion remains the central compiler platform, while language-specific
knowledge lives in independently maintained modules.

### Core design principle

> Fusion should not need to be rewritten every time a new language is
> supported. A new language should be introduced by adding a
> `Lang.<language>.Fusion` module that plugs into the compiler's defined
> interfaces.

------------------------------------------------------------------------

## 2. Architecture and Design Notes

### 2.1 Language modules: `Lang.<language>.Fusion`

Each supported language should have its own language module.

For example:

``` text
Lang.C.Fusion
Lang.CPP.Fusion
Lang.Java.Fusion
Lang.Python.Fusion
Lang.Fusion.Fusion
```

Each module contains the knowledge and rules required to understand its
source language.

A language module should be responsible for:

-   Language identification and supported versions.
-   Lexical rules and token definitions.
-   Grammar and parsing rules.
-   AST node definitions or AST adapter mappings.
-   Type definitions and type resolution.
-   Scope, symbol and name-resolution rules.
-   Language-specific semantic analysis.
-   Language-specific diagnostics and error reporting.
-   Preprocessing and conditional compilation, where applicable.
-   Source-to-source translation rules.
-   Conversion from the source AST into Fusion's target representation.
-   Native compilation support, where applicable.
-   Required runtime, standard-library and ABI integration information.
-   Language-specific tests and compatibility information.

The module may be split into submodules when the language is large. The
public language-module interface should remain consistent regardless of
its internal structure.

For example:

``` text
Lang.C.Fusion/
    LanguageDefinition
    Lexer
    Parser
    AST
    Semantic
    Types
    Preprocessor
    Compiler
    Migration
    Diagnostics
    Tests
```

These names illustrate logical responsibilities; they do not require
every component to be a separate file.

### 2.2 Compiler language injection interface

The main Fusion compiler should expose a defined injection point for
language modules.

The compiler should not contain hard-coded C, C++, Java or Python
parsing logic. It should discover or receive a language module and call
its registered interfaces.

Conceptually:

``` text
Compiler
    |
    +-- LanguageRegistry
    |
    +-- LanguageInjection
    |       |
    |       +-- Load language module
    |       +-- Register lexer/parser
    |       +-- Register AST provider/adapter
    |       +-- Register semantic analyser
    |       +-- Register compiler services
    |       +-- Register migration translator
    |
    +-- Shared compiler services
    |
    +-- Fusion target pipeline
```

The injection interface should define contracts for the following
capabilities:

  Interface               Responsibility
  ----------------------- -------------------------------------------
  `ILanguageModule`       Module identity, version and capabilities
  `ILexerProvider`        Tokenisation rules
  `IParserProvider`       Parsing source into an AST
  `IASTProvider`          Source AST types and node access
  `ISemanticProvider`     Language-specific semantic analysis
  `ITypeProvider`         Type information and type mapping
  `ICompilerProvider`     Native compilation pipeline integration
  `IMigrationProvider`    Translation into Fusion's representation
  `IDiagnosticProvider`   Language-specific errors and warnings

Not every language must implement every capability. For example, a
language module may initially support migration without supporting
native compilation.

The compiler should check module capabilities before starting a
requested operation.

### 2.3 Parser and AST injection

The parser and AST should be independent compiler services with a
language-specific implementation supplied by the injected module.

This is an important separation.

The main compiler defines the interfaces and expected behaviour. The
language module supplies the implementation.

For C:

``` text
C Source
   |
   v
C Lexer
   |
   v
C Parser
   |
   v
C AST
   |
   v
C Semantic Analysis
```

For Java, the same compiler interfaces are used, but the Java module
supplies its own lexer, parser, AST and semantic rules.

The compiler must not assume that every language has the same AST node
types or structure. A C function declaration and a Java method
declaration may represent similar concepts, but they are not identical
language constructs.

The AST provider should expose enough information for downstream
services to inspect nodes without forcing every source language to use
Fusion's internal AST classes.

**Important distinction:**

-   A source AST represents the original language.
-   A migration IR represents the normalised meaning needed for
    translation.
-   A Fusion AST represents valid constructs in the target language.

These are three different responsibilities and should not be collapsed
into one universal AST.

### 2.4 Language-specific AST and rules

Each language module owns its language-specific AST interpretation.

For example, `Lang.C.Fusion` understands:

-   C declarations and declarators.
-   Pointers and pointer arithmetic.
-   Structs and unions.
-   Function declarations and function pointers.
-   Arrays and memory layout.
-   Macros and preprocessing.
-   C scopes and type rules.
-   C expressions and operators.
-   C storage duration and lifetime.
-   C calling conventions and ABI details.

`Lang.CPP.Fusion` would separately understand C++ features such as
classes, templates, constructors, destructors, exceptions, overload
resolution and references.

Do not assume that C++ is simply an extension of the C migration rules.
It can reuse selected infrastructure, but its language semantics need
their own implementation.

The language module should be the authoritative place for explaining and
implementing the source language's rules.

### 2.5 Migration engine and translation rules

The migration engine should be separate from the parser.

Its job is to inspect the source AST and determine how each
source-language construct should be represented in the target language.

For example:

``` text
C AST Node
    FunctionDecl
        |
        v
C-to-Fusion Translator
        |
        v
Fusion FunctionDeclaration
```

The translator should use dedicated handlers for different node types.

Examples:

-   Function declaration translator.
-   Variable declaration translator.
-   Expression translator.
-   Control-flow translator.
-   Type translator.
-   Pointer and reference translator.
-   Memory ownership translator.
-   Struct and union translator.
-   Function-pointer translator.

The translator should not modify the original source AST. It reads the
source nodes and builds new target representations.

A translation rule should be able to provide:

-   The source node or construct it handles.
-   The target Fusion construct.
-   Required semantic information.
-   Conversion logic.
-   Compatibility conditions.
-   Warnings and errors.
-   A human-readable explanation of the conversion.
-   Whether manual review is required.

### 2.6 Migration annotations and explanations

The language module should support metadata or annotations associated
with AST nodes.

This allows the module to document why a source construct is translated
in a particular way.

For example:

``` text
Source Node:
    C: PointerDeclaration

Source:
    int* value;

Translation:
    Target: FusionReference<int>

Explanation:
    C uses explicit pointers.
    Fusion uses ownership-aware references.

Requirements:
    Determine pointer ownership.
    Determine whether the pointer escapes its scope.
    Check whether ownership is transferred.

Status:
    Requires semantic analysis
```

Prefer keeping migration metadata in a sidecar structure keyed by AST
node ID or source location, rather than changing the parser's AST
structures.

This preserves the source AST and allows different translation targets
or migration-rule versions to attach their own metadata.

Annotations should also support diagnostics:

-   Automatic conversion.
-   Conversion requiring review.
-   Unsupported or unsafe conversion.
-   Conversion requiring additional source information.

The compiler or IDE can use this information to show developers exactly
what happened during migration.

### 2.7 Intermediate Representation (Migration IR)

I recommend introducing a migration-specific intermediate representation
between the source AST and Fusion AST.

``` text
Source AST
    |
    v
Migration IR
    |
    v
Fusion AST
```

The Migration IR should represent the meaning and requirements of the
source program without being tied too closely to one source language.

Possible IR concepts include:

-   Functions and callable operations.
-   Variables and values.
-   Types and type relationships.
-   Expressions and control flow.
-   Memory allocations.
-   Ownership and lifetime requirements.
-   Resource management.
-   External dependencies.
-   Calling conventions and interoperability requirements.
-   Source-language metadata and source locations.

The IR is particularly useful when source and target languages have
different memory models.

For example:

-   C uses explicit allocation and deallocation.
-   Java uses garbage collection.
-   Fusion uses its own ownership and lifetime model.

The source-language module interprets the original rules and records the
relevant requirements in the IR. The Fusion translator then determines
how those requirements can be represented using Fusion features.

The IR should retain source-language details whenever they affect
behaviour. It must not discard information merely to make different
languages look identical.

### 2.8 Fusion AST as the target representation

The Fusion AST is the target of migration.

Once the source program has been translated into Fusion constructs, the
Fusion AST should pass through the same semantic validation used by
normal Fusion source code.

This ensures that migrated code follows Fusion's actual language rules.

The process is:

1.  Build Fusion AST nodes.
2.  Resolve Fusion types and symbols.
3.  Validate scopes and declarations.
4.  Validate ownership and lifetimes.
5.  Validate resource and concurrency rules.
6.  Report unsupported or ambiguous conversions.
7.  Generate Fusion source code.

The Fusion compiler remains responsible for deciding whether the
resulting program is valid Fusion.

The migration engine should not bypass Fusion's normal semantic checks.

### 2.9 Source generation and reverse conversion

The Fusion code generator should be responsible for producing readable
`.fusion` source files from the Fusion AST.

This gives the migration system a clean separation:

``` text
C AST → Migration IR → Fusion AST → Fusion Source
```

The same Fusion AST can also be used for normal Fusion-to-Fusion
operations, such as:

-   Parsing and regenerating Fusion source.
-   Normalising source formatting.
-   Upgrading older Fusion syntax to newer syntax.
-   Applying code transformations.
-   Refactoring code.
-   Generating canonical Fusion source.

For true reverse migration, such as Fusion back to C, a separate
Fusion-to-C translator would be needed.

Reverse conversion cannot always be lossless. Fusion may contain
ownership, type-system or runtime features that have no direct C
equivalent. The translator must report these limitations rather than
silently changing behaviour.

### 2.10 Native compilation versus migration

The architecture should explicitly distinguish two operations.

**A. Compile the source language**

The language module supplies the components needed to compile the source
language according to its own language rules.

For example:

``` text
C Source
   |
   v
Lang.C.Fusion
   |
   v
C Parsing and Semantic Analysis
   |
   v
C Compilation Pipeline
   |
   v
Selected Output Target
```

This requires more than a parser. It may require a preprocessor,
standard library, runtime, ABI implementation, linker integration and
target-specific code generation.

The Fusion compiler can orchestrate these components, but it should not
claim full C compatibility until those requirements are implemented.

**B. Migrate the source language to Fusion**

The language module interprets the source language and translates it
into Fusion.

``` text
C Source
   |
   v
Lang.C.Fusion
   |
   v
C AST and Semantic Analysis
   |
   v
C-to-Fusion Migration
   |
   v
Fusion AST
   |
   v
Fusion Code Generator
   |
   v
New Fusion Source
```

The original C source remains unchanged.

These two operations can share the same lexer, parser, AST and semantic
analysis components. Their output pipelines are different.

### 2.11 Fusion as a multi-language compiler

The compiler should support a language registry that can load multiple
language modules.

A possible configuration:

``` text
Compiler Configuration:

    SourceLanguage: C
    SourceVersion: C17

    LanguageModule: Lang.C.Fusion

    Operation: Migrate

    TargetLanguage: Fusion
    TargetVersion: Current

    Output:
        ./Migrated/
```

Another example:

``` text
Compiler Configuration:

    SourceLanguage: Java
    SourceVersion: Java 21

    LanguageModule: Lang.Java.Fusion

    Operation: Migrate

    TargetLanguage: Fusion

    Output:
        ./Migrated/
```

The compiler should support capability discovery, module versioning and
compatibility checks.

Language modules should be independently versioned so that changes to C
migration rules do not unexpectedly affect Java or native Fusion
compilation.

### 2.12 Preserve source fidelity and program behaviour

Migration must be treated as a semantic operation, not a text-conversion
exercise.

Important considerations:

-   Preserve original source files.
-   Retain source locations for diagnostics and traceability.
-   Preserve comments and documentation where possible.
-   Handle macros and conditional compilation explicitly.
-   Preserve external function and library dependencies.
-   Identify ABI and binary-layout requirements.
-   Detect undefined or implementation-dependent source behaviour.
-   Report constructs that cannot be translated safely.
-   Validate generated Fusion code.
-   Use automated tests to compare source and migrated program
    behaviour.

A migration report should record what was converted, what was changed,
what requires review and what could not be converted.

### 2.13 Testing strategy

Each language module should have its own test suite.

For `Lang.C.Fusion`, tests should cover:

-   Tokenisation and parsing.
-   AST structure and source locations.
-   C type resolution.
-   Function and variable translation.
-   Expressions and operators.
-   Loops and conditional statements.
-   Structs, unions and arrays.
-   Pointers and pointer arithmetic.
-   Memory allocation and deallocation.
-   Function pointers.
-   Preprocessor behaviour.
-   External library calls.
-   Ownership and lifetime conversion.
-   Unsupported constructs and diagnostics.

Migration tests should use paired source and expected output files:

``` text
Tests/
    C/
        basic_function.c
        pointer_example.c
        struct_example.c
        memory_example.c

    ExpectedFusion/
        basic_function.fusion
        pointer_example.fusion
        struct_example.fusion
        memory_example.fusion
```

Tests should verify both generated Fusion syntax and program behaviour
where executable test cases are available.

------------------------------------------------------------------------

## 3. Recommended Initial Implementation

I recommend implementing the architecture in the following order.

1.  **Define the language module contract.** Establish the interfaces
    that every language module must expose.
2.  **Build the language injection system.** Load and register language
    modules without hard-coding language-specific logic into the
    compiler.
3.  **Define the source AST provider interface.** Allow each language to
    supply its own AST implementation.
4.  **Implement `Lang.Fusion.Fusion`.** Use Fusion itself as the first
    language module to prove the architecture.
5.  **Define the Migration IR.** Keep it small initially and expand it
    as real translation requirements emerge.
6.  **Implement `Lang.C.Fusion`.** Start with a well-defined subset of
    C.
7.  **Implement C-to-Fusion translation.** Translate basic types,
    functions, variables, expressions and control flow.
8.  **Connect the Fusion AST builder and code generator.** Generate new
    `.fusion` source files.
9.  **Add semantic and ownership conversion.** Handle pointers,
    allocations, lifetimes and resource management carefully.
10. **Add native C compilation support.** Treat this as a separate
    capability from migration.
11. **Expand language support.** Add C++, Java, Python and other
    languages as independent modules.

The first prototype should prove that a language module can be injected,
parse its own source language, provide its own AST and produce Fusion
source without modifying the original source.

------------------------------------------------------------------------

## 4. Architectural Decisions to Keep

The following decisions should guide implementation.

  Decision                      Recommendation
  ----------------------------- ---------------------------------------------------
  Language support              One `Lang.<language>.Fusion` module per language
  Parser                        Supplied by the language module through injection
  AST                           Language-specific source AST
  AST modification              Source AST remains read-only during migration
  Translation                   Implemented by the language module
  Migration metadata            Sidecar annotations associated with AST nodes
  Intermediate representation   Shared migration IR where useful
  Target AST                    Native Fusion AST
  Code generation               Existing Fusion code generator
  Native compilation            Separate language-module capability
  Module structure              May be split into submodules
  Original source               Never overwritten during migration
  Validation                    Always use Fusion's normal semantic pipeline

## 5. Final Architectural Goal

Fusion should become a compiler platform that can understand multiple
programming languages through injectable language modules.

Each `Lang.<language>.Fusion` module is responsible for understanding
its language completely enough to support the capabilities it
advertises.

The main compiler provides the shared infrastructure, orchestration,
injection interfaces and Fusion target pipeline.

This allows new languages to be added without redesigning the compiler
itself.

The long-term goal is:

``` text
                  FUSION COMPILER
                         |
                Language Injection
                         |
          +--------------+--------------+
          |              |              |
       Lang.C         Lang.CPP       Lang.Java
          |              |              |
       C Parser       C++ Parser     Java Parser
          |              |              |
        C AST          C++ AST        Java AST
          |              |              |
       C Rules        C++ Rules      Java Rules
          |              |              |
       C Compiler     C++ Compiler   Java Compiler
          |              |              |
          +--------------+--------------+
                         |
                   Migration IR
                         |
                     Fusion AST
                         |
                 Fusion Compiler
                         |
                  Fusion Output
```

The diagram shows the shared migration route; native compilation can
instead use each language module's own compilation pipeline.

**The central principle:**

Fusion is the compiler platform. Language modules provide
language-specific understanding and compilation rules. The Fusion AST
and code generator provide the common target for migrated code.

A new language should primarily require a new `Lang.<language>.Fusion`
module, not changes to the core Fusion compiler.
