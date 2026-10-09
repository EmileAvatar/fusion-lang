# src/ - the Fusion compiler (Python)

A `.fusion` file goes through these stages, in order (driven by `main.py` in the root):

1. `config/` - load the optional `fusion.toml` project settings
2. `lexer/` - turn source text into tokens
3. `parser/` - turn tokens into an AST (abstract syntax tree)
4. `semantic/` - check names, types and control flow; annotate the AST with types
5. `codegen/` - turn the checked AST into C code, which GCC compiles to an `.exe`

| Folder | What it holds |
|---|---|
| `config/` | Project settings from `fusion.toml` (indentation, source rules, structs, strings) |
| `lexer/` | Tokenizer: keywords, operators, literals, comments, indentation, source security |
| `parser/` | AST node classes and the recursive-descent parser |
| `semantic/` | Symbol table, name resolution, type checking, control-flow and entry-point checks |
| `codegen/` | C code generation, the C runtime for strings, type and name mapping |
| `utils/` | Shared error/diagnostic classes |

Each folder has its own `CLAUDE.md` with one line per file. Keep them current when a file is
added, renamed or changes its job.
