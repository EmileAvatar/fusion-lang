"""Tests for Task 28 - the Fusion compiler written in Fusion (selfhost/).

The Python compiler builds selfhost/main.fusion once; the tests then run that exe.
- Its lexer (28.2): `--tokens` must print exactly the tokens the Python lexer makes, for
  every tier 1 program (task/selfhost_subset.md) - and for every other example too, as the
  lexer is complete.
- The whole compiler (28.3-28.6): each program in SLICES is built by both compilers; both
  programs must print the same and exit the same, and the selfhost-built one passes the
  leak check (-DFUSION_LEAK_CHECK). SLICES grows one program at a time until it is tier 1.
"""

import shutil
import tempfile

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


# The tier 1 programs the selfhost compiler builds so far, in the order they were added
SLICES = ['hello_world',
          # slice 2: functions, parameters, if / while / for range, checked arithmetic, print
          'factorial', 'fizzbuzz', 'max_three', 'sum_array', 'const_demo', 'calculator',
          'syntax_functions_and_blocks',
          # slice 3: string values (owned, copied, freed), floats / chars / bools, format,
          # default and named arguments
          'syntax_strings', 'syntax_variables_and_control_flow', 'syntax_interpolation',
          'syntax_defaults_and_named_args',
          # slice 4: fixed arrays (checked indexes, len, int[] parameters, for over arrays),
          # function values, function types and lambdas
          'arrays_demo', 'functions_demo', 'syntax_lambdas']


def run_exe(exe: Path) -> tuple:
    result = subprocess.run([str(exe), '--headless'], capture_output=True, timeout=60,
                            stdin=subprocess.DEVNULL)
    return result.returncode, result.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')


@pytest.mark.parametrize('name', SLICES)
def test_selfhost_builds_the_program_the_python_compiler_builds(selfhost, name):
    source = ROOT / 'examples' / f'{name}.fusion'
    with tempfile.TemporaryDirectory() as tmp:
        python_dir, selfhost_dir = Path(tmp) / 'python', Path(tmp) / 'selfhost'
        python_dir.mkdir()
        selfhost_dir.mkdir()
        shutil.copy(source, python_dir)
        shutil.copy(source, selfhost_dir)
        built = subprocess.run([sys.executable, str(ROOT / 'main.py'), str(python_dir / source.name)],
                               capture_output=True, text=True, timeout=120)
        assert built.returncode == 0, built.stderr
        built = subprocess.run([str(selfhost), str(selfhost_dir / source.name), '--leak-check',
                                '--runtime', str(ROOT / 'runtime')],
                               capture_output=True, timeout=120)
        assert built.returncode == 0, built.stdout.decode('utf-8', 'replace')
        expected = run_exe(python_dir / f'{name}.exe')
        actual = run_exe(selfhost_dir / f'{name}.exe')
    assert actual == expected     # same output and exit code - and exit 3 / 4 would be a leak
