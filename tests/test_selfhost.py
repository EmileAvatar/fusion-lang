"""Tests for Task 28 - the Fusion compiler written in Fusion (selfhost/).

The Python compiler builds selfhost/main.fusion once; the tests then run that exe.
- Its lexer (28.2): `--tokens` must print exactly the tokens the Python lexer makes, for
  every tier 1 program (task/selfhost_subset.md) - and for every other example too, as the
  lexer is complete.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.lexer import Lexer
from tests.test_runtime_header import TIER_1

ROOT = Path(__file__).resolve().parent.parent
SELFHOST = ROOT / 'selfhost' / 'main.exe'


@pytest.fixture(scope='module')
def selfhost():
    """Build selfhost/main.fusion with the Python compiler (once per test run)."""
    result = subprocess.run([sys.executable, str(ROOT / 'main.py'), str(ROOT / 'selfhost' / 'main.fusion')],
                            capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, result.stdout + result.stderr
    return SELFHOST


def shown(text: str) -> str:
    """The same escaping as the Fusion lexer's dump (selfhost/lexer/lexer.fusion, shown)."""
    text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return '"' + text.replace('\t', '\\t').replace('\r', '\\r') + '"'


def python_tokens(path: Path) -> list:
    """The Python lexer's tokens in the selfhost dump format: KIND "value" line:col."""
    lines = []
    for token in Lexer(path.read_text(encoding='utf-8'), str(path)).tokenize():
        value = shown(token.value)
        if token.type.name == 'STRING_LIT':
            tags = {'STRING_PART': 'S', 'INTERP_VAR': 'V', 'INTERP_POS': 'P'}
            value = ' '.join(tags[kind] + shown(text) for kind, text in json.loads(token.value))
        lines.append(f'{token.type.name} {value} {token.location.line}:{token.location.column}')
    return lines


def selfhost_tokens(exe: Path, path: Path) -> list:
    result = subprocess.run([str(exe), str(path), '--tokens'], capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.decode('utf-8').replace('\r\n', '\n').strip('\n').split('\n')


ALL_EXAMPLES = sorted(p.relative_to(ROOT / 'examples').as_posix()
                      for p in list((ROOT / 'examples').glob('*.fusion'))
                      + list((ROOT / 'examples').glob('*/*.fusion'))
                      + list((ROOT / 'examples').glob('*/*/*.fusion')))


@pytest.mark.parametrize('name', ALL_EXAMPLES)
def test_selfhost_lexer_makes_the_python_lexers_tokens(selfhost, name):
    path = ROOT / 'examples' / name
    expected = python_tokens(path)
    actual = selfhost_tokens(selfhost, path)
    for i, (want, got) in enumerate(zip(expected, actual)):
        assert got == want, f'token {i + 1}'
    assert len(actual) == len(expected)
