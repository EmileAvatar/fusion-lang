"""Tests for Task 28.1.1 - run(command): run another program, wait, return its exit code.

The command goes to the system shell (cmd /c on Windows, /bin/sh -c elsewhere). A program
that runs and fails just returns its code; only a shell that can't start is a ProcessError.
run is in the std layer.
"""

import sys
import tempfile
from pathlib import Path

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_layers import errors_with
from tests.test_structs import main

ROOT = Path(__file__).resolve().parent.parent


def errors(source: str) -> list:
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return [str(e) for e in analyzer.get_errors()]


def quoted(path: Path) -> str:
    """A path as it goes inside a Fusion string: forward slashes, in shell quotes."""
    return '\\"' + path.as_posix() + '\\"'


# ---- the checker

def test_run_takes_text_and_gives_an_int():
    assert errors(main('int code = run("echo hi")')) == []
    assert errors(main('run(5)'))
    assert errors(main('string s = run("echo hi")'))


def test_run_needs_the_std_layer():
    assert any("'run' needs the std layer" in e for e in errors_with('alloc', main('int c = run("x")')))


def test_a_program_may_have_its_own_function_called_run():
    source = 'int function run(int x) : x + 1\n\n' + main('print("{@1}", run(41))')
    code, out, _ = compile_and_run(source)
    assert code == 0 and out.strip() == '42'


def test_process_error_is_a_built_in_error_type():
    source = main('try\n    int c = run("echo x")\ncatch ProcessError e\n    print("{e.kind}")')
    assert errors(source) == []


# ---- running programs

def test_run_returns_the_exit_code():
    code, out, _ = compile_and_run(main('print("{@1} {@2}", run("exit 0"), run("exit 3"))'))
    assert code == 0 and out.strip() == '0 3'


def test_a_command_that_fails_is_not_an_error():
    code, out, _ = compile_and_run(main('int c = run("nosuchprogram_fusion_xyz")\n'
                                        'print("{@1}", c != 0)'))
    assert code == 0 and out.strip().splitlines()[-1] == 'true'


def test_output_stays_in_order():
    code, out, _ = compile_and_run(main('print("before")\nint c = run("echo middle")\nprint("after")'))
    assert code == 0
    assert [line.strip() for line in out.strip().splitlines()] == ['before', 'middle', 'after']


def test_compile_and_run_a_fusion_program_from_fusion():
    """The self-hosted compiler's driver needs exactly this (28.6): call the compiler, then
    run what it made - here through a folder whose name has a space."""
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / 'with space'
        folder.mkdir()
        hello = folder / 'hello.fusion'
        hello.write_text(main('print("Hello from the built program")'), encoding='utf-8')
        exe = hello.with_suffix('.exe')
        body = (f'int built = run("{quoted(Path(sys.executable))} {quoted(ROOT / "main.py")} '
                f'{quoted(hello)}")\n'
                f'int ran = run("{quoted(exe)} --headless")\n'
                f'print("built {{built}}, ran {{ran}}")')
        code, out, err = compile_and_run(main(body))
        assert code == 0, err
        assert 'Hello from the built program' in out
        assert out.strip().splitlines()[-1] == 'built 0, ran 0'
        assert exe.exists()
