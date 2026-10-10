# src/modules/ - modules and `import` (Task 18.4)

| File | Job |
|---|---|
| `loader.py` | Finds module folders, parses each module once, rewrites every file's names to internal ones (`round` -> `money.round`) and merges everything into one program |
| `__init__.py` | Exports `load_program` and `ModuleLoader` |
