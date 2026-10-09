# src/config/ - project settings

| File | What it does |
|---|---|
| `project_config.py` | Finds and validates `fusion.toml` ([indentation], [source], [structs], [strings], [safety], [backend]); a missing file means all defaults, a bad value is an error |
| `__init__.py` | Exports `load_project_config` and the settings classes |
