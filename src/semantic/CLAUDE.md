# src/semantic/ - checking the AST

| File | What it does |
|---|---|
| `semantic_analyzer.py` | Runs the passes below in order and collects errors and warnings (entry point of this folder) |
| `name_resolver.py` | Registers built-ins, structs, functions and variables; reports undefined/duplicate names and unknown types |
| `type_checker.py` | Checks every expression and statement's types; struct, string, array and call rules; writes `inferred_type` |
| `control_flow_validator.py` | Checks returns on every path, and `break`/`continue` only inside loops |
| `entry_point_validator.py` | Checks there is exactly one valid `main` function |
| `symbol.py` | `Symbol` (a named thing) and `Scope` (one block's names) |
| `symbol_table.py` | The stack of scopes: enter/exit blocks, define and look up names |
| `errors.py` | `SemanticError`, used for both errors and warnings |
| `__init__.py` | Exports `SemanticAnalyzer` |
