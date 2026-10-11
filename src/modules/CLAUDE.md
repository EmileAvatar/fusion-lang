# src/modules/ - modules and `import` (Task 18.4)

| File | Job |
|---|---|
| `loader.py` | Finds module folders, parses each module once, rewrites every file's names to internal ones (`round` -> `money.round`), checks `public`, merges everything into one program; `load_program_file` (used by check.py / verify_examples) and module interfaces (`--interface`) |
| `__init__.py` | Exports `load_program`, `load_program_file`, `make_file_parser`, `ModuleLoader`, `module_interface`, `program_interfaces` |
