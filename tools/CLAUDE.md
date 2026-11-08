# tools/ - helper scripts (not part of the compiler)

- `patch.py` - applies a list of exact (file, old, new) edits, all or nothing (Task 22.11)
- `example_subset.py` - lists every construct, type, operator and builtin the examples use (28.1)
- `builtins_doc.py` - makes files/Builtins.md from the compiler's built-ins (28.1.4); used by
  `check.py --builtins` and the "builtins" check
- `doc_nav.py` - writes the navigation line at the top and bottom of the root documents and of
  files/spec/ (order: files/spec/index.md); the "nav" check in check.py (51.5)
- `settings_doc.py` - writes the "Built" part of files/spec/001-TomlSettings.md from
  files/fusionSettings.xml; the "settings" check in check.py (51.5)
- `windows/fusion-file-preview.reg` - Explorer preview pane shows `.fusion` files as text (23.8)
- `windows/fusion-file-preview-undo.reg` - removes that again
