# Fusion Language Specification - Index

The language specification, one topic per file, in reading order. Each file links to the one
before and after it and back here. Being split out of `files/fusion-language-spec.md` one
file at a time (Task 51.5) - a topic not listed yet is still there.

Each major section starts with a `**Status:**` line matching `files/FEATURES.md`: `[DONE n]`
built (task n), `[PARTLY]` some of it built, `[PLANNED n]` scheduled as task n, `[DESIGN]` the
intended design with no task yet. What works today, with examples: `files/SYNTAX_REFERENCE.md`.

000-009 are kept for the high-level files (user, 2026-11-08); the topics start at 010.

| File | What it holds |
|---|---|
| [001 TomlSettings](001-TomlSettings.md) | Every project setting (`fusion.toml`): the built ones (generated) and the decided ones |
| [010 Philosophy](010-Philosophy.md) | The principles every task follows; the three block styles and the source text rules |
| [020 SemanticContract](020-SemanticContract.md) | What every built construct does, in one place - each rule tested |
| [030 Types](030-Types.md) | Value and reference types, every built-in type, nullability, variables, constants |
| [031 Arrays](031-Arrays.md) | Fixed-size arrays: declaring, reading and writing, as parameters and return values |
| [032 Strings](032-Strings.md) | Strings as values: length, ownership, comparison, operations, raw bytes, the string functions |
| [033 TypeCasting](033-TypeCasting.md) | Converting between types: when an int is used as a float, the conversion functions |
| [040 Functions](040-Functions.md) | Declaring functions, main, the block styles, calling - default values, named arguments |
| [041 Lambdas](041-Lambdas.md) | Lambdas and function values (function types) |
| [042 MultipleReturns](042-MultipleReturns.md) | Several return values; an Error returned |

Still in `files/fusion-language-spec.md`:
classes, structs, enums, control flow, null, memory, concurrency, generics, errors,
comments, collections, modules, the game example, building, the standard library, interop,
reserved words, the features summary, the language comparison.
