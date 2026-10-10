# src/codegen/ - checked AST -> C code

| File | What it does |
|---|---|
| `c_generator.py` | `CCodeGenerator`: walks the AST and writes C - statements, expressions, functions, structs, calls (entry point of this folder) |
| `c_memory.py` | The C runtime embedded in every program (strings, UTF-8, run-time errors, leak check) and the rules for copying/freeing strings |
| `c_equality.py` | Lowers `==` `!=` `===` `!==` per type; generates struct / array comparison helpers on demand |
| `c_strings.py` | C for the versatile string functions (Task 18.3.6), appended to the runtime prelude |
| `c_bytes.py` | C for raw bytes (Task 18.3.8): `byte` / `bytes`, appended to the runtime prelude |
| `c_runtime.py` | Lowers built-ins: `print`, `len`, `format` and string interpolation into `printf` / string building |
| `c_types.py` | Maps Fusion types to C types; function-pointer typedefs; wrappers for returned arrays |
| `c_names.py` | Fusion names -> C names: functions / structs get `fu_` (`add` -> `fu_add`), clashing locals too (`auto` -> `fu_auto`), fields only for C keywords; hidden array-length names |
| `__init__.py` | Exports `CCodeGenerator` |
