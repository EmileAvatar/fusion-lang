# src/codegen/ - checked AST -> C code

| File | What it does |
|---|---|
| `c_generator.py` | `CCodeGenerator`: walks the AST and writes C - statements, expressions, functions, structs, calls (entry point of this folder) |
| `c_memory.py` | The C runtime embedded in every program (strings, UTF-8, run-time errors, leak check) and the rules for copying/freeing strings |
| `c_runtime.py` | Lowers built-ins: `print`, `len`, `format` and string interpolation into `printf` / string building |
| `c_types.py` | Maps Fusion types to C types; function-pointer typedefs; wrappers for returned arrays |
| `c_names.py` | Renames identifiers that clash with C keywords (`double` -> `fusion_double`); hidden array-length names |
| `__init__.py` | Exports `CCodeGenerator` |
