"""Fusion's syntax highlighting for editors (Task 36.0, 36.1) - one TextMate grammar, written from the lexer's own tables.

    python tools/editors/build_grammar.py           write the grammar files
    python tools/editors/build_grammar.py --check   the grammar files match the lexer (the "editors" check in check.py)
    python tools/editors/build_grammar.py --vsix    also pack the VS Code extension: tools/editors/fusion-lang.vsix

The keywords and reserved words come from src/lexer/keywords.py, so a new keyword is highlighted once this runs;
the words that are keywords only in their place (byVal, readonly, step, foreach ...) are listed here. Written:
- vscode-fusion/syntaxes/fusion.tmLanguage.json  VS Code (with vscode-fusion/package.json, language-configuration.json)
- sublime/Fusion.tmLanguage                      Sublime Text and TextMate (an XML plist - the same grammar)
- sublime/Comments.tmPreferences                 Sublime: // and /* */ for comment toggling
Fusion's colours (36.8) come from colors.json - change a colour there and run this again. Written from it:
- vscode-fusion/themes/fusion-<palette>-color-theme.json  four VS Code colour themes (and their list in package.json)
- sublime/Fusion-<Palette>.sublime-color-scheme           the same four for Sublime Text
- files/tutorial/fusion-code.css                          the site's code colours (light; colour-safe under .colour-safe)
"""
import json
import plistlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.lexer.keywords import KEYWORDS, RESERVED_WORDS  # noqa: E402

HERE = Path(__file__).resolve().parent
VSCODE = HERE / 'vscode-fusion'
SUBLIME = HERE / 'sublime'
SITE_CSS = ROOT / 'files' / 'tutorial' / 'fusion-code.css'
COLORS = HERE / 'colors.json'
VERSION = '0.1.2'

# Each keyword by kind - the scope a theme colours it by
CONTROL = {'if', 'else', 'for', 'while', 'loop', 'End', 'end', 'break', 'continue', 'return', 'match', 'case',
           'try', 'catch', 'finally', 'throw', 'go', 'async', 'await'}
DECLARATION = {'function', 'func', 'class', 'struct', 'interface', 'enum', 'Enum', 'inherits', 'implements',
               'property', 'get', 'set', 'import', 'new', 'cast', 'namespace'}
MODIFIER = {'public', 'private', 'internal', 'protected', 'static', 'virtual', 'override', 'abstract', 'sealed',
            'const', 'let', 'var', 'service', 'fixed', 'Shared', 'Weak'}
TYPE = {'int', 'float', 'double', 'string', 'bool', 'char', 'byte', 'short', 'long', 'int128', 'int256', 'void'}
OPERATOR_WORD = {'and', 'or', 'not', 'is', 'in'}
LITERAL = {'true', 'false', 'null'}
THIS = {'this'}

# Words that are keywords only in their place (the parser reads them there) - highlighted as keywords
IN_PLACE = {
    'control': ['foreach', 'step', 'fall'],      # not run: also the built-in run("program")
    'declaration': ['constructor', 'extends', 'includes', 'template'],
    'modifier': ['byVal', 'byRef', 'readonly', 'nocopy', 'noshare'],
    'variable': ['super'],
}
# Built-in type names that aren't keywords
BUILTIN_TYPES = ['bytes', 'decimal', 'money', 'Rounding', 'List', 'Map', 'Dictionary', 'Collection', 'Iterator', 'Entry', 'Error', 'Default',
                 'Cloneable', 'Number']


def _words(words) -> str:
    return '|'.join(sorted(set(words), key=lambda w: (-len(w), w)))


def grammar() -> dict:
    kinds = [CONTROL, DECLARATION, MODIFIER, TYPE, OPERATOR_WORD, LITERAL, THIS]
    unsorted = set(KEYWORDS) - set().union(*kinds)
    if unsorted:      # a new keyword in the lexer: give it a kind here (the check fails until then)
        raise SystemExit(f'build_grammar.py: give these keywords a kind: {sorted(unsorted)}')
    word = r'(?<![\w.])\b({})\b'
    return {
        '$schema': 'https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json',
        'name': 'Fusion',
        'scopeName': 'source.fusion',
        'fileTypes': ['fusion'],
        'comment': 'Written by tools/editors/build_grammar.py from src/lexer/keywords.py - do not edit by hand',
        'patterns': [{'include': '#comments'}, {'include': '#strings'}, {'include': '#chars'},
                     {'include': '#numbers'}, {'include': '#declarations'}, {'include': '#keywords'},
                     {'include': '#types'}, {'include': '#calls'}, {'include': '#operators'}],
        'repository': {
            'comments': {'patterns': [
                {'name': 'comment.block.fusion', 'begin': r'/\*', 'end': r'\*/'},
                {'name': 'comment.line.double-slash.fusion', 'match': r'//.*$'}]},
            'strings': {'patterns': [{
                'name': 'string.quoted.double.fusion', 'begin': '"', 'end': '"',
                'patterns': [
                    {'name': 'constant.character.escape.fusion', 'match': r'\\(u\{[0-9A-Fa-f]+\}|u[0-9A-Fa-f]{4}|.)'},
                    {'name': 'meta.interpolation.fusion', 'match': r'(\{)(@\d+|[^{}"]+)(\})',
                     'captures': {'1': {'name': 'punctuation.section.interpolation.begin.fusion'},
                                  '2': {'name': 'variable.other.interpolated.fusion'},
                                  '3': {'name': 'punctuation.section.interpolation.end.fusion'}}}]}]},
            'chars': {'patterns': [{'name': 'string.quoted.single.fusion',
                                    'match': r"'(\\(u\{[0-9A-Fa-f]+\}|u[0-9A-Fa-f]{4}|.)|[^'\\])'"}]},
            'numbers': {'patterns': [
                {'name': 'constant.numeric.hex.fusion', 'match': r'\b0[xX][0-9A-Fa-f_]+\b'},
                {'name': 'constant.numeric.binary.fusion', 'match': r'\b0[bB][01_]+\b'},
                {'name': 'constant.numeric.octal.fusion', 'match': r'\b0[oO][0-7_]+\b'},
                {'name': 'constant.numeric.decimal.fusion', 'match': r'\b\d[\d_]*\.\d[\d_]*([eE][+-]?\d+)?\b'},
                {'name': 'constant.numeric.integer.fusion', 'match': r'\b\d[\d_]*\b'}]},
            'declarations': {'patterns': [
                {'match': r'\b(function|func)\s+([A-Za-z_]\w*)',
                 'captures': {'1': {'name': 'storage.type.function.fusion'}, '2': {'name': 'entity.name.function.fusion'}}},
                {'match': r'\b(class|struct|interface|enum|Enum)\s+([A-Za-z_]\w*)',
                 'captures': {'1': {'name': 'storage.type.class.fusion'}, '2': {'name': 'entity.name.type.fusion'}}}]},
            'keywords': {'patterns': [
                {'name': 'keyword.control.fusion', 'match': word.format(_words(CONTROL | set(IN_PLACE['control'])))},
                {'name': 'storage.type.fusion', 'match': word.format(_words(DECLARATION | set(IN_PLACE['declaration'])))},
                {'name': 'storage.modifier.fusion', 'match': word.format(_words(MODIFIER | set(IN_PLACE['modifier'])))},
                {'name': 'keyword.operator.word.fusion', 'match': word.format(_words(OPERATOR_WORD))},
                {'name': 'constant.language.fusion', 'match': word.format(_words(LITERAL))},
                {'name': 'variable.language.fusion', 'match': word.format(_words(THIS | set(IN_PLACE['variable'])))},
                {'name': 'keyword.other.reserved.fusion', 'match': word.format(_words(RESERVED_WORDS))}]},
            'types': {'patterns': [
                {'name': 'support.type.primitive.fusion', 'match': word.format(_words(TYPE))},
                {'name': 'support.class.builtin.fusion', 'match': word.format(_words(BUILTIN_TYPES))},
                {'name': 'entity.name.type.fusion', 'match': r'\b[A-Z][A-Za-z0-9_]*\b'}]},
            'calls': {'patterns': [{'match': r'\b([a-z_][A-Za-z0-9_]*)\s*(?=\()',
                                    'captures': {'1': {'name': 'entity.name.function.call.fusion'}}}]},
            'operators': {'patterns': [
                {'name': 'keyword.operator.range.fusion', 'match': r'\.\.\.'},
                {'name': 'keyword.operator.null.fusion', 'match': r'\?\.|\?\?'},
                {'name': 'keyword.operator.comparison.fusion', 'match': r'===|!==|==|!=|<=|>='},
                {'name': 'keyword.operator.arrow.fusion', 'match': r'->|=>'},
                {'name': 'keyword.operator.fusion', 'match': r'[-+*/%=<>!&|^~?:]'}]},
        },
    }


def comments_preferences() -> dict:
    return {'name': 'Comments', 'scope': 'source.fusion', 'settings': {'shellVariables': [
        {'name': 'TM_COMMENT_START', 'value': '// '},
        {'name': 'TM_COMMENT_START_2', 'value': '/*'}, {'name': 'TM_COMMENT_END_2', 'value': '*/'}]}}


# ---------------------------------------------------------------- colours (36.8)

def colors() -> dict:
    return json.loads(COLORS.read_text(encoding='ascii'))


def _title(key: str) -> str:
    """'colour-safe-dark' -> 'Colour-Safe-Dark'."""
    return '-'.join(part.capitalize() for part in key.split('-'))


def _json(data) -> bytes:
    return (json.dumps(data, indent=2) + '\n').encode('ascii')


def vscode_theme(palette: dict, roles: dict) -> dict:
    """A VS Code colour theme: Fusion's token colours on the editor's own default look (dark or light)."""
    token_colors = []
    for role, look in palette['colors'].items():
        settings = {'foreground': look['color']}
        if look.get('style'):
            settings['fontStyle'] = look['style']
        token_colors.append({'name': role, 'scope': roles[role]['scopes'], 'settings': settings})
    return {'name': palette['name'], 'type': palette['type'],
            'colors': {'editor.background': palette['background'], 'editor.foreground': palette['foreground']},
            'tokenColors': token_colors}


def sublime_scheme(palette: dict, roles: dict) -> dict:
    dark = palette['type'] == 'dark'
    rules = []
    for role, look in palette['colors'].items():
        rule = {'name': role, 'scope': ', '.join(roles[role]['scopes']), 'foreground': look['color']}
        if look.get('style'):
            rule['font_style'] = look['style']
        rules.append(rule)
    return {'name': palette['name'],
            'globals': {'background': palette['background'], 'foreground': palette['foreground'],
                        'caret': palette['foreground'], 'selection': '#264F78' if dark else '#ADD6FF',
                        'line_highlight': '#2A2D2E' if dark else '#F3F3F3'},
            'rules': rules}


def _css_look(look: dict) -> str:
    style = look.get('style', '')
    parts = [f'color: {look["color"]};']
    if 'bold' in style:
        parts.append('font-weight: 600;')
    if 'italic' in style:
        parts.append('font-style: italic;')
    if 'underline' in style:
        parts.append('text-decoration: underline;')
    return ' '.join(parts)


def site_css(data: dict) -> str:
    """The site's code colours: the light palette, the colour-safe light one under `.colour-safe` (a switch later)."""
    roles = data['roles']
    light, safe = data['palettes']['light'], data['palettes']['colour-safe-light']
    lines = ['/* Fusion code blocks - the colours of Fusion source on every page of the site.',
             '   Written by tools/editors/build_grammar.py from tools/editors/colors.json - change a colour there, not here',
             '   (the same colours as the editors). A block: <pre class="fusion"><code> ... </code></pre>, each part in a',
             '   span: kw (keyword), type, fn (function name), str (string), num (number), com (comment), op (operator).',
             '   A page (or body) with class="colour-safe" uses the colour-blind safe palette. */',
             '',
             'pre.fusion {',
             '  margin: 0;',
             '  padding: 12px 16px;',
             f'  background: {light["background"].lower()};',
             '  border: 1px solid #d9dee3;',
             '  overflow-x: auto;',
             '  font-family: Consolas, "Courier New", monospace;',
             '  font-size: 15px;',
             '  line-height: 1.5;',
             '}',
             'pre.fusion code { background: none; padding: 0; }',
             '']
    site_roles = [(role, spec['site']) for role, spec in roles.items() if 'site' in spec]
    for role, cls in site_roles:
        lines.append(f'pre.fusion .{cls} {{ {_css_look(light["colors"][role])} }}')
    lines.append('')
    for role, cls in site_roles:
        lines.append(f'.colour-safe pre.fusion .{cls} {{ {_css_look(safe["colors"][role])} }}')
    return '\n'.join(lines) + '\n'


def package_json(data: dict) -> dict:
    themes = [{'label': p['name'], 'uiTheme': 'vs-dark' if p['type'] == 'dark' else 'vs',
               'path': f'./themes/fusion-{key}-color-theme.json'} for key, p in data['palettes'].items()]
    return {
        'name': 'fusion-lang',
        'displayName': 'Fusion Language',
        'description': 'Syntax highlighting and colour themes for the Fusion programming language (Tasks 36.0, 36.8)',
        'version': VERSION,
        'publisher': 'fusion-lang',
        'license': 'SEE LICENSE IN the Fusion repository',
        'repository': {'type': 'git', 'url': 'https://github.com/EmileAvatar/fusion-lang'},
        'engines': {'vscode': '^1.71.0'},
        'categories': ['Programming Languages', 'Themes'],
        'contributes': {
            'languages': [{'id': 'fusion', 'aliases': ['Fusion', 'fusion'], 'extensions': ['.fusion'],
                           'configuration': './language-configuration.json',
                           'icon': {'light': './icons/fusion.svg', 'dark': './icons/fusion.svg'}}],
            'grammars': [{'language': 'fusion', 'scopeName': 'source.fusion',
                          'path': './syntaxes/fusion.tmLanguage.json'}],
            'themes': themes,
        },
    }


def outputs() -> dict:
    """path -> the bytes it should hold."""
    g = grammar()
    data = colors()
    written = {
        VSCODE / 'syntaxes' / 'fusion.tmLanguage.json': _json(g),
        SUBLIME / 'Fusion.tmLanguage': plistlib.dumps({k: v for k, v in g.items() if k != '$schema'}),
        SUBLIME / 'Comments.tmPreferences': plistlib.dumps(comments_preferences()),
        VSCODE / 'package.json': _json(package_json(data)),
        SITE_CSS: site_css(data).encode('ascii'),
    }
    for key, palette in data['palettes'].items():
        written[VSCODE / 'themes' / f'fusion-{key}-color-theme.json'] = _json(vscode_theme(palette, data['roles']))
        written[SUBLIME / f'Fusion-{_title(key)}.sublime-color-scheme'] = _json(sublime_scheme(palette, data['roles']))
    return written


MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="fusion-lang" Version="{version}" Publisher="fusion-lang" />
    <DisplayName>Fusion Language</DisplayName>
    <Description xml:space="preserve">Syntax highlighting for the Fusion programming language</Description>
    <Categories>Programming Languages</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.71.0" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
'''
CONTENT_TYPES = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json" />
  <Default Extension=".vsixmanifest" ContentType="text/xml" />
  <Default Extension=".md" ContentType="text/markdown" />
  <Default Extension=".svg" ContentType="image/svg+xml" />
</Types>
'''


def pack_vsix() -> Path:
    """The VS Code extension as a .vsix (a zip) - `code --install-extension tools/editors/fusion-lang.vsix`."""
    target = HERE / 'fusion-lang.vsix'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('extension.vsixmanifest', MANIFEST.format(version=VERSION))
        for path in sorted(VSCODE.rglob('*')):
            if path.is_file():
                z.write(path, 'extension/' + path.relative_to(VSCODE).as_posix())
    return target


def main(argv) -> int:
    wanted = outputs()
    if '--check' in argv:
        stale = [p for p, data in wanted.items() if not p.exists() or p.read_bytes() != data]
        for p in stale:
            print(f'{p.relative_to(ROOT)} is out of date - fix: python tools/editors/build_grammar.py')
        return 1 if stale else 0
    for path, data in wanted.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f'wrote {path.relative_to(ROOT)}')
    if '--vsix' in argv:
        print(f'wrote {pack_vsix().relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
