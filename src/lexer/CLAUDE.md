# src/lexer/ - source text -> tokens

| File | What it does |
|---|---|
| `lexer.py` | The `Lexer` class: walks the source and produces the token list (entry point of this folder) |
| `token.py` | `Token`, `TokenType` and `SourceLocation` (file, line, column) definitions |
| `keywords.py` | The reserved-word table: maps words like `if`, `struct`, `int` to token types |
| `operators.py` | Recognises operators and punctuation (`+`, `==`, `->`, `.`, brackets) |
| `literals.py` | Numbers, strings (incl. `{name}` / `{@N}` interpolation parts, escapes) and char literals |
| `comments.py` | Skips `//` and `/* */` comments |
| `indentation.py` | Tracks indentation and emits INDENT / DEDENT tokens (tab width, mixed tabs/spaces) |
| `block_style.py` | Tracks which of the three block styles (indentation, braces, `End`) is in use |
| `source_security.py` | Rejects invisible/bidirectional characters and look-alike identifiers (Task 19.6) |
| `__init__.py` | Exports `Lexer` and the token types |
