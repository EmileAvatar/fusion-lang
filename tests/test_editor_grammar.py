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
            'extension/syntaxes/fusion.tmLanguage.json'} <= names
