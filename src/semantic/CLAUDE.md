# src/semantic/ - checking the AST

| File | What it does |
|---|---|
| `semantic_analyzer.py` | Runs the passes below in order and collects errors and warnings (entry point of this folder) |
| `number_patterns.py` | Checks `formatNumber` patterns written in the source (the same rules as the C runtime) |
| `templates.py` | String templates (Task 29.3): runs first and expands every use - `greet(a)` becomes `format(<text>, a)`, a template passed where a function type is written becomes a lambda (`expand_templates`) |
| `struct_parents.py` | Structs building on structs (Task 32.8): gives `struct Employee implements Person` its Person part (`expand_struct_parents`, run before name resolution), and the type rules - inherited fields and methods, an Employee as a Person, constructors, a whole struct as text, `toCSV` (a mixin of the type checker) |
| `enums.py` | Enums (Task 25): turns enum types / `Color.Red` / `Color.values()` into enum nodes before checking (`normalize_enums`), checks declarations, and the type rules (a mixin of the type checker) |
| `error_rules.py` | Errors (Task 26): turns `Error` types / `Error(...)` into error nodes (`normalize_errors`), and the type rules - fields, `if err`, `return Error(...)` (a mixin of the type checker) |
| `collection_rules.py` | Type rules for `List<T>` and `Map<K, V>` (Tasks 18.5.1-2): literals, methods, `for x in` - a mixin of the type checker |
| `name_resolver.py` | Registers built-ins (and their optional arguments, `BUILTIN_DEFAULTS`), structs, functions and variables; reports undefined/duplicate names and unknown types |
| `type_checker.py` | Checks every expression and statement's types; struct, string, array and call rules; writes `inferred_type` |
| `control_flow_validator.py` | Checks returns on every path, and `break`/`continue` only inside loops |
| `entry_point_validator.py` | Checks there is exactly one valid `main` function |
| `symbol.py` | `Symbol` (a named thing) and `Scope` (one block's names) |
| `symbol_table.py` | The stack of scopes: enter/exit blocks, define and look up names |
| `errors.py` | `SemanticError`, used for both errors and warnings |
| `__init__.py` | Exports `SemanticAnalyzer` |
