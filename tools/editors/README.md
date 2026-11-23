# Editor support - syntax highlighting for Fusion (Task 36)

One TextMate grammar, written by `build_grammar.py` from the compiler's own keyword table
(`src/lexer/keywords.py`) - a new keyword is highlighted once it runs, and `python check.py` (the `editors` check)
fails while the grammar is out of date. Don't edit the written files by hand.

| Folder | For |
|---|---|
| `vscode-fusion/` | VS Code: `package.json`, `language-configuration.json` (comments, brackets, folding, indenting), `syntaxes/fusion.tmLanguage.json` |
| `sublime/` | Sublime Text and TextMate: `Fusion.tmLanguage` (the same grammar as an XML plist), `Comments.tmPreferences` (comment toggling) |

## Install

**VS Code:**
```text
python tools/editors/build_grammar.py --vsix
code --install-extension tools/editors/fusion-lang.vsix --force
```
then reload VS Code (Ctrl+Shift+P - "Developer: Reload Window"). Remove: `code --uninstall-extension fusion-lang.fusion-lang`.

**Sublime Text:** copy the `sublime/` folder to Sublime's Packages folder as `Fusion`
(Windows: `%APPDATA%\Sublime Text\Packages\Fusion`; macOS: `~/Library/Application Support/Sublime Text/Packages/Fusion`),
then open a `.fusion` file - View > Syntax shows Fusion.

## What is highlighted
Keywords by kind (control, declaration, modifier, operator words, literals, reserved words), the words that are
keywords only in place (`byVal`, `readonly`, `step`, `foreach` ...), types (built in, and any capitalised name),
function names (declared, and before `(`), strings with `{name}` / `{@1}` and escapes, chars, numbers (`0x`, `0b`,
`0o`, `_`, decimals - `1...10` stays a range), `//` and `/* */` comments, operators (`...`, `?.`, `??`, `===`).
