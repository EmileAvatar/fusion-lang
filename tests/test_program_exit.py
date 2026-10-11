"""A compiled program waits for a key before its window closes (user request 2026-10-11) -
unless it is run with --headless, or no one is at the console (input or output
redirected, as in these tests). The wait itself needs a real console, so the tests check
the generated C and that redirected and --headless runs end by themselves."""

import os
import subprocess
import tempfile

from tests.test_structs import generate_c, main
from src.codegen.c_memory import RUNTIME_PRELUDE


def test_main_receives_the_arguments():
    c_code = generate_c(main('print("hi")'))
    assert 'int main(int argc, char** argv) {' in c_code
    assert 'fusion_init(argc, argv);' in c_code


def test_the_wait_is_skipped_headless_or_without_a_console():
    assert 'strcmp(argv[i], "--headless") == 0' in RUNTIME_PRELUDE
    assert 'FUSION_IS_CONSOLE(stdin) && FUSION_IS_CONSOLE(stdout)' in RUNTIME_PRELUDE
    assert 'atexit(fusion_wait_for_key)' in RUNTIME_PRELUDE


def test_redirected_and_headless_runs_end_by_themselves():
    c_code = generate_c(main('print("done")'))
    with tempfile.TemporaryDirectory() as tmp:
        c_file, exe = os.path.join(tmp, 'p.c'), os.path.join(tmp, 'p.exe')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        build = subprocess.run(['gcc', '-Wall', '-Wextra', c_file, '-o', exe],
                               capture_output=True, text=True)
        assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr
        for args in ([exe], [exe, '--headless']):
            result = subprocess.run(args, capture_output=True, text=True, timeout=20)
            assert (result.returncode, result.stdout) == (0, 'done\n')
            assert 'Press any key' not in result.stderr
