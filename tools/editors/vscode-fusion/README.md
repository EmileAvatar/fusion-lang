# Fusion Language - VS Code

Syntax highlighting for `.fusion` files (Task 36.0): keywords, types, function and type names, strings with
`{name}` / `{@1}` interpolation, chars, numbers, comments and operators; comment toggling (Ctrl+/), brackets,
auto-closing quotes, folding (all three block styles are indented), indenting after a block line.

The grammar is written by `tools/editors/build_grammar.py` from the compiler's own keyword table - don't edit
`syntaxes/fusion.tmLanguage.json` by hand.

Install: `python tools/editors/build_grammar.py --vsix`, then `code --install-extension tools/editors/fusion-lang.vsix`
and reload VS Code (Ctrl+Shift+P - Developer: Reload Window).
