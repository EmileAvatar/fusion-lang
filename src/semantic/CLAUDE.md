# src/semantic/ - checking the AST

| File | What it does |
|---|---|
| `semantic_analyzer.py` | Runs the passes below in order and collects errors and warnings (entry point of this folder) |
| `number_patterns.py` | Checks `formatNumber` patterns written in the source (the same rules as the C runtime) |
| `templates.py` | String templates (Task 29.3): runs first and expands every use - `greet(a)` becomes `format(<text>, a)`, a template passed where a function type is written becomes a lambda (`expand_templates`) |
| `struct_parents.py` | Structs building on structs (Task 32.8): gives `struct Employee implements Person` its Person part (`expand_struct_parents`, run before name resolution), and the type rules - inherited fields and methods, an Employee as a Person, constructors, a whole struct as text, `toCSV` (a mixin of the type checker) |
| `inferred.py` | `let` / `var` and match values (Task 46): the type from the value, a let or var set later (`check_set_once` - set before read, a let once), the type rules of a match that gives a value (a mixin of the type checker) |
| `readonly.py` | readonly parameters (Task 32.2e): after type checking, finds what each function does with each parameter (change, keep, pass on - following the calls) and reports any of it on a readonly one |
| `setup_blocks.py` | Form B on any variable (Task 32.2d): a local's set-up block becomes a block right after its declaration; checks a set-up block (local or class field) changes only its own variable |
| `statics.py` | A class's statics (Task 32.2c): each static becomes a module variable `Car.count` and the class's set-up (forms A, B, C) the function `Car.__setup` (`expand_statics`, before name resolution); after type checking `static_setup_order` orders the set-ups by dependency and reports a circle |
| `class_rules.py` | Class rules over the whole program (Task 32.10d): a warning for each circle of classes whose objects can hold each other - never freed under OWNERSHIP (`check_class_cycles`); constructors (32.2b); `[visibility] required` - a missing level is an error (`check_visibility_written`, 32.2h) |
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
