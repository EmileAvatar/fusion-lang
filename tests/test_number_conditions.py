"""Tests for Task 30.9 - numbers as conditions: `[conditions] numbers` in fusion.toml.

"positive" (default): in an `if` / `while` condition a number is true when above zero - zero
and negatives (-1: "not found", "not set") are false. "nonzero": 0 false, any other number
true (C, Python, JavaScript). "off": a condition must be a bool. Inside a condition, `and` /
`or` / `not` follow the same rule, and `count == true` compares by it; `count === true` is
always false (a number is not a bool), and `bool b = count` is an error in every mode.
"""

import os
import subprocess

import pytest

from src.codegen import CCodeGenerator
from src.config import ConditionsConfig, ProjectConfigError, load_project_config
from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from tests.test_structs import main

PROGRAM = main('int count = 3\n'
               'int zero = 0\n'
               'int found = -1\n'
               'bool ready = true\n'
               'string out = ""\n'
               'if count\n'
               '    out = out + "count "\n'
               'if zero\n'
               '    out = out + "zero "\n'
               'if found\n'
               '    out = out + "found "\n'
               'if count and ready\n'
               '    out = out + "and "\n'
               'if not zero\n'
               '    out = out + "not "\n'
               'if found == true\n'
               '    out = out + "eq "\n'
               'int left = 3\n'
               'while left\n'
               '    left = left - 1\n'
               'print("{out}{left}")')


def analyze(source: str, numbers: str):
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer(conditions_config=ConditionsConfig(numbers=numbers))
    analyzer.analyze(program)
    return analyzer, program


def run(source: str, numbers: str, tmp_path) -> str:
    analyzer, program = analyze(source, numbers)
    assert not analyzer.get_errors(), analyzer.get_errors()
    c_file, exe = os.path.join(tmp_path, 'out.c'), os.path.join(tmp_path, 'out.exe')
    with open(c_file, 'w', encoding='utf-8') as f:
        f.write(CCodeGenerator().generate(program))
    build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', c_file, '-o', exe],
                           capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    result = subprocess.run([exe], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def errors(source: str, numbers: str) -> list:
    return [str(e) for e in analyze(source, numbers)[0].get_errors()]


def test_positive_is_the_default(tmp_path):
    assert ConditionsConfig().numbers == 'positive'
    assert run(PROGRAM, 'positive', tmp_path) == 'count and not 0'   # -1 is false


def test_nonzero_like_c_and_python(tmp_path):
    assert run(PROGRAM, 'nonzero', tmp_path) == 'count found and not eq 0'   # -1 is true


def test_off_needs_a_bool():
    found = errors(PROGRAM, 'off')
    assert any('If condition must be bool, got int' in e for e in found)
    assert any('While condition must be bool, got int' in e for e in found)


@pytest.mark.parametrize('numbers', ['positive', 'nonzero', 'off'])
def test_a_number_never_becomes_a_bool_outside_a_condition(numbers):
    assert any('Cannot assign int to variable of type bool' in e
               for e in errors(main('int count = 3\nbool b = count'), numbers))


def test_triple_equals_with_a_bool_is_always_false():
    program = Parser(Lexer(main('int count = 3\nif count === true\n    print("x")'),
                           'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    assert any("'===' is always false here: int and bool" in str(w)
               for w in analyzer.get_warnings())


def test_the_setting_in_fusion_toml(tmp_path):
    source = tmp_path / 'main.fusion'
    source.write_text('')
    (tmp_path / 'fusion.toml').write_text('[conditions]\nnumbers = "nonzero"\n')
    assert load_project_config(str(source)).conditions.numbers == 'nonzero'
    (tmp_path / 'fusion.toml').write_text('[conditions]\nnumbers = "maybe"\n')
    with pytest.raises(ProjectConfigError, match='conditions.numbers must be one of'):
        load_project_config(str(source))
