# Editor support - syntax highlighting for Fusion (Task 36)

One TextMate grammar, written by `build_grammar.py` from the compiler's own keyword table
(`src/lexer/keywords.py`) - a new keyword is highlighted once it runs, and `python check.py` (the `editors` check)
fails while the grammar is out of date. Don't edit the written files by hand.

| Folder | For |
|---|---|
| `vscode-fusion/` | VS Code: `package.json`, `language-configuration.json` (comments, brackets, folding, indenting), `syntaxes/fusion.tmLanguage.json` |
| `sublime/` | Sublime Text and TextMate: `Fusion.tmLanguage` (the same grammar as an XML plist), `Comments.tmPreferences` (comment toggling), the four colour schemes |
| `colors.json` | Fusion's colours - the one file to change them (below) |

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

## Fusion's colours (36.8)
`colors.json` holds every colour in one place: the roles (keyword, declaration, modifier, type, function, string,
escape, interpolation, number, comment, operator, literal, this, reserved - each the grammar scopes it colours) and
four palettes:

| Palette | For |
|---|---|
| Fusion Dark / Fusion Light | the everyday look |
| Fusion Colour-Safe Dark / Light | colour-blind safe: the Okabe-Ito colours (safe for the three common kinds of colour blindness), fewer colours, told apart by style too |

- Colour is never the only signal: keywords are bold, comments italic, reserved words underlined
- Every colour reaches WCAG AA contrast (4.5:1) on its background - `tests/test_editor_grammar.py` checks it
- Written from it by `build_grammar.py`: the four VS Code themes (`vscode-fusion/themes/`, listed in `package.json`),
  four Sublime colour schemes (`sublime/Fusion-*.sublime-color-scheme`) and the site's `files/tutorial/fusion-code.css`
- Choose one - VS Code: Ctrl+K Ctrl+T (Preferences: Color Theme) - "Fusion Dark" ...; Sublime: Preferences > Select
  Color Scheme - "Fusion-Dark" ...
- To change a colour for everyone: edit `colors.json`, run `python tools/editors/build_grammar.py --vsix`, reinstall

## Changing a colour in your own editor only
The grammar only names each piece (`keyword.control.fusion`, `string.quoted.double.fusion` ...); the theme
gives the colours - so Fusion code works with any theme. To change one in your own VS Code, without touching the
project - in settings.json:
```json
"editor.tokenColorCustomizations": {
  "textMateRules": [
    { "scope": "keyword.control.fusion", "settings": { "foreground": "#0072B2", "fontStyle": "bold" } }
  ]
}
```

## What is highlighted
Keywords by kind (control, declaration, modifier, operator words, literals, reserved words), the words that are
keywords only in place (`byVal`, `readonly`, `step`, `foreach` ...), types (built in, and any capitalised name),
function names (declared, and before `(`), strings with `{name}` / `{@1}` and escapes, chars, numbers (`0x`, `0b`,
`0o`, `_`, decimals - `1...10` stays a range), `//` and `/* */` comments, operators (`...`, `?.`, `??`, `===`).
