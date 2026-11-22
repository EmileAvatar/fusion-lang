# src/parser/ - tokens -> AST

| File | What it does |
|---|---|
| `parser.py` | The recursive-descent `Parser`: expressions (by precedence), statements, functions, structs, enums |
| `list_methods.py` | A List of your own (33.3d1, D.174): the List methods Fusion adds to a class implementing `List<T>`, written in Fusion from its core five |
| `ast_nodes.py` | Every AST node class (expressions, statements, declarations, types); the semantic pass fills in `inferred_type` |
| `__init__.py` | Exports `Parser`, `ParserError` and the AST node classes |
