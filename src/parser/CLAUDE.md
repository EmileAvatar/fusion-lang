# src/parser/ - tokens -> AST

| File | What it does |
|---|---|
| `parser.py` | The recursive-descent `Parser`: expressions (by precedence), statements, functions, structs |
| `ast_nodes.py` | Every AST node class (expressions, statements, declarations, types); the semantic pass fills in `inferred_type` |
| `__init__.py` | Exports `Parser`, `ParserError` and the AST node classes |
