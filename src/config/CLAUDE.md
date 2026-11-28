# src/config/ - project settings

| File | What it does |
|---|---|
| `project_config.py` | Validates the project settings (every section - see `files/fusionSettings.xml`); a missing file means all defaults (or a new fusion.toml), a bad value is an error; `[project] fusionSettingFormat` changes the file's format |
| `settings_files.py` | The settings file in four formats (Task 31): finds it (TOML, YAML, JSON, INI), reads each into one dictionary, writes them, the master template `files/fusionSettings.xml`, a new default fusion.toml, changing format with a .bak backup |
| `settings_block.py` | A `Fusion.Settings { ... }` block first in a file (Task 58.2, D.224): read into the same dictionary a settings file gives (the name alone or `section.name`, from files/fusionSettings.xml), and blanked out of the source for the lexer |
| `__init__.py` | Exports `load_project_config` and the settings classes |
