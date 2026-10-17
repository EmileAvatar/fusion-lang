"""Tests for Task 27 - semantic contract and safety.

27.1: fixed-size arrays are bounds-checked - reading and writing, local arrays, `int[]`
parameters, struct array fields, arrays of structs, returned arrays and array literals.
Outside the array is a catchable IndexError, never a crash or a silent overwrite. Every
program runs under the leak check.
"""

import pytest

from tests.test_structs import generate_c, main
from tests.test_strings import run_ok
from tests.test_error_handling import run_failing


# ---------------------------------------------------------------- 27.1 array bounds

def test_every_kind_of_array_is_checked():
    assert run_ok(
        'struct Team\n    string name\n    int[3] scores\n'
        'int function pick(int[] values, int i)\n    return values[i]\n'
        'int[2] function pair() : [7, 8]\n'
        + main(
            'int[3] a = [1, 2, 3]\n'
            'Team t = Team("x", [4, 5, 6])\n'
            'Team[2] teams = [t, t]\n'
            'for i in [-1, 3, 9]\n'
            '    for step in range(0, 6)\n'
            '        try\n'
            '            match step\n'
            '                case 0: print("{@1}", a[i])\n'
            '                case 1: a[i] = 9\n'
            '                case 2: print("{@1}", pick(a, i))\n'
            '                case 3: print("{@1}", t.scores[i])\n'
            '                case 4: print("{@1}", teams[i].scores[0])\n'
            '                else: print("{@1}", pair()[i])\n'
            '        catch IndexError e\n'
            '            print("{step}: {e}")\n'
            '        catch e\n'
            '            print("other")\n'
            'print("{@1} {@2} {@3}", a[0], [7, 8, 9][2], pair()[1])')
    ) == [f'{step}: index {i} is outside the array (length {n})'
          for i in (-1, 3, 9) for step, n in enumerate((3, 3, 3, 3, 2, 2))] + ['1 9 8']


def test_an_array_literal_can_be_indexed():
    # 27.1b: [1, 2][i] used to generate invalid C
    assert run_ok(main(
        'int i = 1\n'
        'string s = ["a", "b"][i]\n'
        'print("{@1} {s}", [10, 20, 30][i + 1])'
    )) == ['30 b']


def test_an_out_of_range_write_never_changes_anything():
    assert run_ok(main(
        'int[2] a = [1, 2]\n'
        'int[2] b = [3, 4]\n'
        'try\n'
        '    a[2] = 99\n'
        'catch e\n'
        '    print("{e.kind}")\n'
        'print("{@1} {@2} {@3} {@4}", a[0], a[1], b[0], b[1])'
    )) == ['IndexError', '1 2 3 4']


def test_an_uncaught_array_index_stops_the_program():
    lines, stderr = run_failing(main('int[3] a = [1, 2, 3]\nint i = 3\nprint("{@1}", a[i])'))
    assert 'Runtime error at test.fusion:4: index 3 is outside the array (length 3)' in stderr


def test_a_written_index_inside_the_array_needs_no_check():
    c_code = generate_c(main('int[3] a = [1, 2, 3]\nprint("{@1}", a[2])'))
    assert 'fusion_index(' not in c_code.split('int main')[-1]
    c_code = generate_c(main('int[3] a = [1, 2, 3]\nint i = 2\nprint("{@1}", a[i])'))
    assert 'fusion_index(i, 3, ' in c_code


# ---------------------------------------------------------------- 27.4 the three block styles

def test_the_three_block_styles_compile_to_the_same_c():
    """examples/style_indent / style_braces / style_end: one program written with
    indentation, braces and End keywords must give identical C - only the source positions
    in run-time error messages ("style_end.fusion:12") may differ (user request, Task 27.4)."""
    import re
    from pathlib import Path
    from src.lexer import Lexer
    from src.parser.parser import Parser
    from src.semantic import SemanticAnalyzer
    from src.codegen import CCodeGenerator
    examples = Path(__file__).resolve().parent.parent / 'examples'
    outputs = {}
    for style in ('indent', 'braces', 'end'):
        path = examples / f'style_{style}.fusion'
        source = path.read_text(encoding='utf-8')
        ast = Parser(Lexer(source, str(path)).tokenize()).parse_program()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), analyzer.get_errors()
        c_code = CCodeGenerator().generate(ast)
        outputs[style] = re.sub(r'"style_\w+\.fusion:\d+"', '"WHERE"', c_code)
    assert outputs['indent'] == outputs['braces'] == outputs['end']


# ---------------------------------------------------------------- 27.2b overflow, 27.2d wrapping

def test_whole_number_overflow_is_an_error():
    assert run_ok(main(
        'int big = 2147483647\n'
        'int low = -2147483647 - 1\n'
        'for step in range(0, 5)\n'
        '    try\n'
        '        match step\n'
        '            case 0: print("{@1}", big + 1)\n'
        '            case 1: print("{@1}", low - 1)\n'
        '            case 2: print("{@1}", big * 2)\n'
        '            case 3: print("{@1}", -low)\n'
        '            else: print("{@1}", low / -1)\n'
        '    catch OverflowError e\n'
        '        print("{e}")\n'
        'print("{@1} {@2} {@3}", big - 1, low + 1, 60 * 60 * 24)'
    )) == ["2147483647 + 1 doesn't fit in an int", "-2147483648 - 1 doesn't fit in an int",
           "2147483647 * 2 doesn't fit in an int", "-(-2147483648) doesn't fit in an int",
           "-2147483648 / -1 doesn't fit in an int", '2147483646 -2147483647 86400']


def test_an_overflow_is_an_arithmetic_error():
    assert run_ok(main(
        'int big = 2147483647\n'
        'try\n'
        '    print("{@1}", big + big)\n'
        'catch ArithmeticError e\n'
        '    print("{e.kind}")'
    )) == ['OverflowError']


def test_wrapping_on_purpose():
    assert run_ok(
        'int function hash(string text)\n'
        '    int h = 17\n'
        '    unchecked\n'
        '        for c in [1, 2, 3, 4, 5, 6, 7]\n'
        '            h = h * 1000003 + c\n'
        '    return h\n'
        + main(
            'int big = 2147483647\n'
            'print("{@1} {@2} {@3}", wrapAdd(big, 1), wrapSub(-big - 1, 1), wrapMul(big, 2))\n'
            'print("{@1} {@2}", big.wrapAdd(2), hash("x"))\n'
            'unchecked {\n'
            '    int w = big + 1\n'
            '    print("{w}")\n'
            '}')
    ) == ['-2147483648 2147483647 -2', f'-2147483647 {_wrapped_hash()}', '-2147483648']


def _wrapped_hash() -> int:
    h = 17
    for c in range(1, 8):
        h = (h * 1000003 + c) & 0xFFFFFFFF
    return h - (1 << 32) if h >= 1 << 31 else h


def test_unsafe_mode_wraps_and_keeps_bounds_checks():
    from tests.test_end_to_end import compile_and_run
    exit_code, stdout, stderr = compile_and_run(main(
        'int big = 2147483647\n'
        'print("{@1} {@2}", big + 1, big * 2)\n'
        'int[2] a = [1, 2]\n'
        'try\n'
        '    print("{@1}", a[big + 3])\n'
        'catch e\n'
        '    print("{e.kind}")'), safety_mode='unsafe')
    assert exit_code == 0, stderr
    assert stdout.splitlines() == ['-2147483648 -2', 'IndexError']


def test_numbers_written_in_the_source_need_no_check():
    c_code = generate_c(main('int day = 60 * 60 * 24\nprint("{day}")'))
    assert 'fusion_mul_int(' not in c_code.split('int main')[-1]


# ---------------------------------------------------------------- 27.2c endless recursion

ENDLESS = ('int function down(int n)\n'
           '    string held = "x" + toString(n)\n'
           '    return down(n + 1) + len(held)\n'
           'int function ping(int n) : pong(n + 1)\n'          # two functions calling each other
           'int function pong(int n) : ping(n + 1)\n'
           'int function fact(int n)\n'
           '    if n <= 1\n'
           '        return 1\n'
           '    return n * fact(n - 1)\n')

USES = main('print("{@1}", fact(10))\n'
            'try\n'
            '    print("{@1}", down(0))\n'
            'catch StackOverflowError e\n'
            '    print("{e.kind}: {e}")\n'
            'int n, err = ping(0)\n'
            'print("{err.kind} {n}")\n'
            'print("still running")')


def test_endless_recursion_is_a_catchable_error():
    lines = run_ok(ENDLESS + USES)
    assert lines == ['3628800', 'StackOverflowError: down() went too deep - the stack is full '
                     '(does it call itself without end?)', 'StackOverflowError 0', 'still running']


def test_call_depth_mode_counts_calls():
    from src.lexer import Lexer
    from src.parser.parser import Parser
    from src.semantic import SemanticAnalyzer
    from src.codegen import CCodeGenerator
    source = ENDLESS + USES
    ast = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    assert SemanticAnalyzer().analyze(ast)
    c_code = CCodeGenerator(max_call_depth=500).generate(ast)
    assert 'fusion_call_depth >= 500' in c_code and 'fu_down__body' in c_code
    import os, subprocess, tempfile
    with tempfile.TemporaryDirectory() as tmp:
        c_file, exe = os.path.join(tmp, 't.c'), os.path.join(tmp, 't.exe')
        open(c_file, 'w', encoding='utf-8').write(c_code)
        build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', c_file, '-o', exe, '-lm'],
                               capture_output=True, text=True)
        assert build.returncode == 0, build.stderr
        run = subprocess.run([exe, '--headless'], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL, timeout=30)
    assert run.returncode == 0, run.stderr
    assert 'down() went past [safety] max_call_depth = 500 calls' in run.stdout


def test_only_functions_that_can_recurse_are_checked():
    c_code = generate_c('int function twice(int n) : n + n\n'
                        + 'int function fact(int n)\n    if n <= 1\n        return 1\n    return n * fact(n - 1)\n'
                        + main('print("{@1} {@2}", twice(2), fact(3))'))
    assert c_code.count('if (fusion_stack_low())') == 1


def test_max_call_depth_in_fusion_toml(tmp_path):
    from src.config import load_project_config, ProjectConfigError
    source = str(tmp_path / 'p.fusion')
    assert load_project_config(source).max_call_depth is None
    (tmp_path / 'fusion.toml').write_text('[safety]\nmax_call_depth = 10000\n')
    assert load_project_config(source).max_call_depth == 10000
    (tmp_path / 'fusion.toml').write_text('[safety]\nmax_call_depth = "max"\n')
    assert load_project_config(source).max_call_depth is None
    (tmp_path / 'fusion.toml').write_text('[safety]\nmax_call_depth = 0\n')
    with pytest.raises(ProjectConfigError, match='max_call_depth must be "max" or a whole number'):
        load_project_config(source)
