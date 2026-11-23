"""Fusion's syntax highlighting for editors (Task 36.0, 36.1) - one TextMate grammar, written from the lexer's own tables.

    python tools/editors/build_grammar.py           write the grammar files
    python tools/editors/build_grammar.py --check   the grammar files match the lexer (the "editors" check in check.py)
    python tools/editors/build_grammar.py --vsix    also pack the VS Code extension: tools/editors/fusion-lang.vsix

The keywords and reserved words come from src/lexer/keywords.py, so a new keyword is highlighted once this runs;
the words that are keywords only in their place (byVal, readonly, step, foreach ...) are listed here. Written:
- vscode-fusion/syntaxes/fusion.tmLanguage.json  VS Code (with vscode-fusion/package.json, language-configuration.json)
- sublime/Fusion.tmLanguage                      Sublime Text and TextMate (an XML plist - the same grammar)
- sublime/Comments.tmPreferences                 Sublime: // and /* */ for comment toggling
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
VERSION = '0.1.0'

# Each keyword by kind - the scope a theme colours it by
CONTROL = {'if', 'else', 'for', 'while', 'loop', 'End', 'end', 'break', 'continue', 'return', 'match', 'case',
           'try', 'catch', 'finally', 'throw', 'go', 'async', 'await'}
DECLARATION = {'function', 'func', 'class', 'struct', 'interface', 'enum', 'Enum', 'inherits', 'implements',
               'property', 'get', 'set', 'import', 'new', 'cast', 'namespace'}
MODIFIER = {'public', 'private', 'internal', 'protected', 'static', 'virtual', 'override', 'abstract', 'sealed',
            'const', 'let', 'var', 'service', 'fixed', 'Shared', 'Weak'}
TYPE = {'int', 'float', 'double', 'string', 'bool', 'char', 'byte', 'short', 'long', 'void'}
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
BUILTIN_TYPES = ['bytes', 'List', 'Map', 'Dictionary', 'Collection', 'Iterator', 'Entry', 'Error', 'Default',
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


def outputs() -> dict:
    """path -> the bytes it should hold."""
    g = grammar()
    return {
        VSCODE / 'syntaxes' / 'fusion.tmLanguage.json': (json.dumps(g, indent=2) + '\n').encode('ascii'),
        SUBLIME / 'Fusion.tmLanguage': plistlib.dumps({k: v for k, v in g.items() if k != '$schema'}),
        SUBLIME / 'Comments.tmPreferences': plistlib.dumps(comments_preferences()),
    }


MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="fusion-lang" Version="{version}" Publisher="fusion-lang" />
    <DisplayName>Fusion Language</DisplayName>
    <Description xml:space="preserve">Syntax highlighting for the Fusion programming language</Description>
    <Categories>Programming Languages</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.60.0" />
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
