"""Task 36.0 / 36.1 - the editors' grammar (tools/editors/build_grammar.py): one TextMate grammar for VS Code and
Sublime Text, written from the lexer's keyword table, so a new keyword can't be left out."""

import importlib.util
import json
import plistlib
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('build_grammar', ROOT / 'tools' / 'editors' / 'build_grammar.py')
build_grammar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_grammar)

from src.lexer.keywords import KEYWORDS, RESERVED_WORDS  # noqa: E402


def rules(grammar):
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key in ('match', 'begin', 'end'):
                if key in node:
                    found.append(node[key])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(grammar)
    return found


def test_every_keyword_and_reserved_word_is_highlighted():
    grammar = build_grammar.grammar()
    text = json.dumps(grammar)
    for word in list(KEYWORDS) + list(RESERVED_WORDS):
        assert re.search(rf'[|(]{re.escape(word)}[|)]', text), word


def test_every_rule_compiles():
    for pattern in rules(build_grammar.grammar()):
        re.compile(pattern)


def first_scope(code: str, rule_names) -> str:
    grammar = build_grammar.grammar()
    for name in rule_names:
        for rule in grammar['repository'][name]['patterns']:
            if 'match' in rule and 'name' in rule and re.fullmatch(rule['match'], code):
                return rule['name']
    return ''


def test_the_scopes():
    assert first_scope('if', ['keywords']) == 'keyword.control.fusion'
    assert first_scope('byVal', ['keywords']) == 'storage.modifier.fusion'
    assert first_scope('step', ['keywords']) == 'keyword.control.fusion'
    assert first_scope('int', ['types']) == 'support.type.primitive.fusion'
    assert first_scope('List', ['types']) == 'support.class.builtin.fusion'
    assert first_scope('Car', ['types']) == 'entity.name.type.fusion'
    assert first_scope('0x6B', ['numbers']) == 'constant.numeric.hex.fusion'
    assert first_scope('3.25e2', ['numbers']) == 'constant.numeric.decimal.fusion'
    assert first_scope('...', ['operators']) == 'keyword.operator.range.fusion'
    assert first_scope('??', ['operators']) == 'keyword.operator.null.fusion'
    assert first_scope("'a'", ['chars']) == 'string.quoted.single.fusion'


def test_a_range_is_not_a_decimal():
    # 1...10 - the number stops before the dots
    decimal = build_grammar.grammar()['repository']['numbers']['patterns'][3]['match']
    assert re.search(decimal, '1...10') is None


def test_interpolation_inside_a_string():
    string = build_grammar.grammar()['repository']['strings']['patterns'][0]
    inside = string['patterns'][1]['match']
    assert [m.group(2) for m in re.finditer(inside, '"{name} is {@1}"')] == ['name', '@1']


def test_the_files_written_match_and_load():
    for path, data in build_grammar.outputs().items():
        assert path.read_bytes() == data, f'{path} - run python tools/editors/build_grammar.py'
    assert plistlib.loads((build_grammar.SUBLIME / 'Fusion.tmLanguage').read_bytes())['scopeName'] == 'source.fusion'
    package = json.loads((build_grammar.VSCODE / 'package.json').read_text(encoding='utf-8'))
    assert package['contributes']['languages'][0]['extensions'] == ['.fusion']
    json.loads((build_grammar.VSCODE / 'language-configuration.json').read_text(encoding='utf-8'))


def test_the_vsix_holds_the_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(build_grammar, 'HERE', tmp_path)
    with zipfile.ZipFile(build_grammar.pack_vsix()) as z:
        names = set(z.namelist())
    assert {'extension.vsixmanifest', '[Content_Types].xml', 'extension/package.json',
            'extension/syntaxes/fusion.tmLanguage.json',
            'extension/themes/fusion-colour-safe-dark-color-theme.json'} <= names


# ---------------------------------------------------------------- Fusion's colours (36.8)

def grammar_scopes() -> set:
    found = set()

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get('name'), str) and node['name'].endswith('.fusion'):
                found.add(node['name'])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(build_grammar.grammar()['repository'])
    return found


def covered(scope: str, roles: dict) -> bool:
    return any(scope == s or scope.startswith(s + '.') for spec in roles.values() for s in spec['scopes'])


def test_every_scope_the_grammar_uses_has_a_colour():
    roles = build_grammar.colors()['roles']
    assert [s for s in sorted(grammar_scopes()) if not covered(s, roles)] == []


def test_every_palette_colours_every_role():
    data = build_grammar.colors()
    for key, palette in data['palettes'].items():
        assert set(palette['colors']) == set(data['roles']), key
        for look in palette['colors'].values():
            assert re.fullmatch(r'#[0-9A-Fa-f]{6}', look['color'])
            assert set(look.get('style', '').split()) <= {'bold', 'italic', 'underline'}


def _luminance(colour: str) -> float:
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    light, dark = sorted([_luminance(a), _luminance(b)], reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_every_colour_meets_wcag_aa_contrast():
    # 4.5:1 against the palette's background - readable for low vision too
    for key, palette in build_grammar.colors()['palettes'].items():
        for role, look in palette['colors'].items():
            assert contrast(look['color'], palette['background']) >= 4.5, (key, role, look['color'])


def test_colour_is_never_the_only_signal():
    # keywords bold and comments italic in every palette, so they are told apart by their style too
    for palette in build_grammar.colors()['palettes'].values():
        assert 'bold' in palette['colors']['keyword'].get('style', '')
        assert 'italic' in palette['colors']['comment'].get('style', '')


def test_the_themes_and_schemes_written():
    data = build_grammar.colors()
    package = json.loads((build_grammar.VSCODE / 'package.json').read_text(encoding='ascii'))
    assert [t['label'] for t in package['contributes']['themes']] == [p['name'] for p in data['palettes'].values()]
    theme = json.loads((build_grammar.VSCODE / 'themes' / 'fusion-light-color-theme.json').read_text(encoding='ascii'))
    keyword = next(t for t in theme['tokenColors'] if t['name'] == 'keyword')
    assert keyword['settings'] == {'foreground': '#0B5CAD', 'fontStyle': 'bold'}
    scheme = json.loads((build_grammar.SUBLIME / 'Fusion-Colour-Safe-Dark.sublime-color-scheme').read_text(encoding='ascii'))
    assert scheme['globals']['background'] == '#1E1E1E'
    css = build_grammar.SITE_CSS.read_text(encoding='ascii')
    assert 'pre.fusion .kw { color: #0B5CAD; font-weight: 600; }' in css
    assert '.colour-safe pre.fusion .kw { color: #0072B2; font-weight: 600; }' in css
