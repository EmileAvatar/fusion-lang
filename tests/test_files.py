"""Tests for Task 18.5.5 - files: readText / readLines / writeText / appendText / readBytes /
writeBytes / fileExists / deleteFile.

Programs run under the leak check in a temporary folder (relative paths are relative to
it), including file names with accents.
"""

import os
import subprocess
import tempfile

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from tests.test_structs import errors_of, main


def run_in(folder: str, source: str):
    """(exit code, stdout lines, stderr) of a program run with `folder` as its working folder."""
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(program), analyzer.get_errors()
    c_code = CCodeGenerator().generate(program)
    c_file, exe = os.path.join(folder, 'p.c'), os.path.join(folder, 'p.exe')
    with open(c_file, 'w', encoding='utf-8') as f:
        f.write(c_code)
    build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', '-Wall', '-Wextra', c_file, '-o', exe],
                           capture_output=True, text=True)
    assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr
    result = subprocess.run([exe], cwd=folder, capture_output=True, timeout=20, stdin=subprocess.DEVNULL)
    return result.returncode, result.stdout.decode('utf-8').splitlines(), result.stderr.decode('utf-8')


def test_write_read_append_text():
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_in(tmp, main(
            'writeText("notes.txt", "one\\ntwo\\n")\n'
            'appendText("notes.txt", "three")\n'
            'string text = readText("notes.txt")\n'
            'List<string> rows = readLines("notes.txt")\n'
            'print("{@1} {@2} {@3} {@4}", len(text), rows.len(), rows[2], fileExists("notes.txt"))\n'
            'writeText("notes.txt", "replaced")\n'
            'print(readText("notes.txt"))'
        ))
        assert code == 0, err
        assert out == ['13 3 three true', 'replaced']
        with open(os.path.join(tmp, 'notes.txt'), 'rb') as f:
            assert f.read() == b'replaced'


def test_text_is_written_byte_for_byte():
    """No newline translation, and UTF-8 text stays UTF-8."""
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_in(tmp, main('writeText("u.txt", "caf\\u00e9\\r\\nb\\n")'))
        assert code == 0, err
        with open(os.path.join(tmp, 'u.txt'), 'rb') as f:
            assert f.read() == 'caf\u00e9\r\nb\n'.encode('utf-8')


def test_accented_file_names_and_bytes():
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_in(tmp, main(
            'bytes data = [0x00, 0xFF, 0x41]\n'
            'writeBytes("caf\\u00e9.bin", data)\n'
            'bytes back = readBytes("caf\\u00e9.bin")\n'
            'print("{@1} {@2} {@3}", back == data, back.rawToHex(), fileExists("caf\\u00e9.bin"))\n'
            'deleteFile("caf\\u00e9.bin")\n'
            'print("{@1}", fileExists("caf\\u00e9.bin"))'
        ))
        assert code == 0, err
        assert out == ['true 00ff41 true', 'false']


def test_byte_order_mark_and_windows_lines():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'bom.txt'), 'wb') as f:
            f.write(b'\xef\xbb\xbfhello\r\nworld\r\n')
        code, out, err = run_in(tmp, main(
            'string t = readText("bom.txt")\n'
            'List<string> rows = readLines("bom.txt")\n'
            'print("{@1} [{@2}] [{@3}] {@4}", len(t), rows[0], rows[1], rows.len())'
        ))
        assert code == 0, err
        assert out == ['14 [hello] [world] 2']


def test_file_exists_is_false_for_folders_and_missing_files():
    with tempfile.TemporaryDirectory() as tmp:
        os.mkdir(os.path.join(tmp, 'sub'))
        code, out, err = run_in(tmp, main('print("{@1} {@2}", fileExists("sub"), fileExists("nope.txt"))'))
        assert (code, out) == (0, ['false false'])


def test_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_in(tmp, main(
            'writeText("e.txt", "")\n'
            'print("[{@1}] {@2} {@3}", readText("e.txt"), readLines("e.txt").len(), len(readBytes("e.txt")))'
        ))
        assert (code, out) == (0, ['[] 0 0'])


@pytest.mark.parametrize("statement, message", [
    ('string t = readText("missing.txt")', "readText: can't open 'missing.txt'"),
    ('bytes b = readBytes("missing.bin")', "readBytes: can't open 'missing.bin'"),
    ('deleteFile("missing.txt")', "deleteFile: can't delete 'missing.txt'"),
    ('writeBytes("bin.dat", hexToRaw("ff00"))\nstring t = readText("bin.dat")',
     "readText: 'bin.dat' is not valid text - use readBytes for a binary file"),
    ('writeText("no_such_folder/x.txt", "x")', "writeText: can't open 'no_such_folder/x.txt'"),
])
def test_run_time_errors(statement, message):
    with tempfile.TemporaryDirectory() as tmp:
        code, out, err = run_in(tmp, main(statement))
        assert code == 1 and message in err, err


def test_argument_types():
    assert "Argument 2 to 'writeText': expected string, got int" in errors_of(main('writeText("a", 5)'))
    assert "Argument 2 to 'writeBytes': expected bytes, got string" in errors_of(main('writeBytes("a", "x")'))
