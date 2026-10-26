"""Tests for Task 28.1.3 - the C run-time as a shared header, runtime/fusion_runtime.h.

The Python compiler normally writes the whole run-time into every C file. With
CCodeGenerator(runtime_include="fusion_runtime.h") it writes only the settings and an
#include of the shared header - the shape the Fusion-written compiler will produce. Each
tier-1 example (task/selfhost_subset.md) is built both ways; both must print the same.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

from src.codegen import CCodeGenerator
from src.codegen.c_generator import runtime_header_text
from src.config import load_project_config
from src.modules.loader import load_program_file
from src.semantic import SemanticAnalyzer

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'runtime'

# Tier 1 of the self-hosting test run (task/selfhost_subset.md)
TIER_1 = ['hello_world', 'factorial', 'fizzbuzz', 'max_three', 'sum_array', 'const_demo',
          'calculator', 'arrays_demo', 'functions_demo', 'structs_demo', 'syntax_strings',
          'syntax_variables_and_control_flow', 'syntax_interpolation',
          'syntax_defaults_and_named_args', 'syntax_functions_and_blocks', 'syntax_lambdas',
          'syntax_structs', 'syntax_equality']


def c_code(path: Path, **options) -> str:
    config = load_project_config(str(path))
    program, errors = load_program_file(str(path), config)
    assert not errors, errors
    analyzer = SemanticAnalyzer(structs_config=config.structs, strings_config=config.strings,
                                stdlib_config=config.stdlib, errors_config=config.errors,
                                numbers_config=config.numbers, modules_config=config.modules)
    assert analyzer.analyze(program), analyzer.get_errors()
    return CCodeGenerator(encoding=config.strings.encoding,
                          max_length=config.strings.max_length,
                          safety_mode=config.safety_mode, max_call_depth=config.max_call_depth,
                          **options).generate(program)


def build_and_run(code: str, folder: Path, name: str) -> tuple:
    source = folder / f'{name}.c'
    exe = folder / f'{name}.exe'
    source.write_text(code, encoding='utf-8')
    gcc = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', f'-I{RUNTIME}', str(source), '-o', str(exe),
                          '-lm'], capture_output=True, text=True, timeout=60)
    assert gcc.returncode == 0, gcc.stderr
    run = subprocess.run([str(exe), '--headless'], capture_output=True, text=True,
                         encoding='utf-8', errors='replace', stdin=subprocess.DEVNULL, timeout=30)
    return run.returncode, run.stdout


def test_the_committed_header_is_up_to_date():
    assert (RUNTIME / 'fusion_runtime.h').read_text(encoding='utf-8') == runtime_header_text()


def test_a_program_using_the_header_has_no_runtime_inside():
    code = c_code(ROOT / 'examples' / 'hello_world.fusion', runtime_include='fusion_runtime.h')
    assert '#include "fusion_runtime.h"' in code
    assert 'static inline fusion_string fusion_str_make' not in code
    full = c_code(ROOT / 'examples' / 'hello_world.fusion')
    assert len(code.splitlines()) < 100 < len(full.splitlines())


def test_settings_come_before_the_header():
    with tempfile.TemporaryDirectory() as tmp:
        program = Path(tmp) / 'p.fusion'
        program.write_text('void function main()\n    print("hi")\n', encoding='utf-8')
        (Path(tmp) / 'fusion.toml').write_text('[strings]\nmax_length = 100\n', encoding='utf-8')
        code = c_code(program, runtime_include='fusion_runtime.h')
    assert code.index('#define FUSION_MAX_LENGTH 100') < code.index('#include "fusion_runtime.h"')


@pytest.mark.parametrize('name', TIER_1)
def test_tier_1_examples_print_the_same_with_the_shared_header(name):
    path = ROOT / 'examples' / f'{name}.fusion'
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        inline = build_and_run(c_code(path), folder, 'inline')
        shared = build_and_run(c_code(path, runtime_include='fusion_runtime.h'), folder, 'shared')
    assert inline[0] == 0
    assert shared == inline
