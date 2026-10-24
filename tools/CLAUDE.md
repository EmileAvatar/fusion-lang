# tools/ - helper scripts (not part of the compiler)

- `patch.py` - applies a list of exact (file, old, new) edits, all or nothing (Task 22.11)
- `example_subset.py` - lists every construct, type, operator and builtin the examples use (28.1)
- `builtins_doc.py` - makes files/Builtins.md from the compiler's built-ins (28.1.4); used by
  `check.py --builtins` and the "builtins" check
- `windows/fusion-file-preview.reg` - Explorer preview pane shows `.fusion` files as text (23.8)
- `windows/fusion-file-preview-undo.reg` - removes that again
