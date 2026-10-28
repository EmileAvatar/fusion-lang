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
        '    print("{e.kind}")'), overflow_wrap=True)   # was [safety] mode = "unsafe" (32.0)
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
    assert 'down() went past [safety] maxCallDepth = 500 calls' in run.stdout


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
    with pytest.raises(ProjectConfigError, match='maxCallDepth must be "max" or a whole number'):
        load_project_config(source)


# ---------------------------------------------------------------- 27.3 features together

def test_a_struct_holding_collections_and_enums_is_a_value():
    assert run_ok(
        'enum Role\n    Admin\n    Guest(string invitedBy)\n'
        'struct Team\n    string name\n    List<string> members\n    Map<string, Role> roles\n'
        'Team function renamed(Team t, string name)\n'
        '    t.name = name\n'                        # a parameter changed: the caller's stays
        '    t.members.add("new")\n'
        '    return t\n'
        + main(
            'Team a = Team("A", ["ada", "bo"], Map<string, Role>())\n'
            'a.roles["ada"] = Role.Admin\n'
            'a.roles["bo"] = Role.Guest("ada")\n'
            'Team b = a\n'                            # a deep copy
            'b.members[0] = "zed"\n'
            'b.roles["bo"] = Role.Admin\n'
            'Team c = renamed(a, "C")\n'
            'print("{a.name} {@1} {@2} {@3}", a.members[0], a.members.len(), a.roles["bo"])\n'
            'print("{b.name} {@1} {@2}", b.members[0], b.roles["bo"])\n'
            'print("{c.name} {@1} {@2}", c.members.len(), c == a)\n'
            'match a.roles["bo"]\n'
            '    case Guest(by): print("invited by {by}")\n'
            '    else: print("?")\n'
            'List<Team> teams = [a, b, c]\n'
            'teams[1].members.add("x")\n'
            'print("{@1} {@2}", teams[1].members.len(), b.members.len())')
    ) == ['A ada 2 Guest', 'A zed Admin', 'C 3 false', 'invited by ada', '3 2']


def test_nested_collections():
    assert run_ok(main(
        'Map<string, List<int>> scores\n'
        'scores["ada"] = [1, 2]\n'
        'scores["bo"] = List<int>()\n'
        'scores["ada"].add(3)\n'
        'scores["bo"].add(9)\n'
        'List<List<string>> grid = [["a", "b"], ["c"]]\n'
        'grid[1].add("d")\n'
        'List<List<string>> copy = grid\n'
        'copy[0][0] = "z"\n'
        'int total = 0\n'
        'for name in scores\n'
        '    for s in scores[name]\n'
        '        total = total + s\n'
        'print("{total} {@1} {@2} {@3}", grid[0][0], copy[0][0], grid[1].join(""))'
    )) == ['15 a z cd']


def test_an_error_through_everything_frees_everything():
    assert run_ok(
        'error ParseError\n    int line\n'
        'struct Doc\n    string title\n    List<string> lines\n'
        'Doc function parse(List<string> raw)\n'
        '    Doc d = Doc("t", List<string>())\n'
        '    int number = 0\n'
        '    for line in raw\n'
        '        number = number + 1\n'
        '        string clean = line.trim()\n'
        '        match clean\n'
        '            case "": continue\n'
        '            case "!": throw ParseError("bang", line = number)\n'
        '            else: d.lines.add(clean)\n'
        '    return d\n'
        + main(
            'List<List<string>> inputs = [[" a ", "", "b"], ["x", "!", "y"]]\n'
            'for input in inputs\n'
            '    try\n'
            '        Doc d = parse(input)\n'
            '        print("{@1} lines", d.lines.len())\n'
            '    catch ParseError e\n'
            '        print("{e} on line {e.line}")\n'
            '    finally\n'
            '        print("done")')
    ) == ['2 lines', 'done', 'bang on line 2', 'done']


def test_early_exits_with_owned_values():
    assert run_ok(
        'string function first(List<string> words, string start)\n'
        '    for w in words\n'
        '        string lower = w.toLower()\n'
        '        if lower.startsWith(start)\n'
        '            return lower\n'
        '    return ""\n'
        + 'int function count(List<string> words)\n'
        '    int n = 0\n'
        '    for w in words\n'
        '        string copy = w + "!"\n'
        '        if w == "stop"\n'
        '            break\n'
        '        if w == "skip"\n'
        '            continue\n'
        '        n = n + len(copy)\n'
        '    return n\n'
        + main('print("{@1} {@2}", first(["Apple", "Banana"], "ba"), count(["ab", "skip", "c", "stop", "zz"]))')
    ) == ['banana 5']


def test_across_modules(tmp_path):
    from tests.test_modules import run_project
    assert run_project(tmp_path, {
        'shapes/shapes.fusion': (
            'public enum Shape\n'
            '    Circle(int r)\n'
            '    Box(int w, int h)\n'
            'public error ShapeError\n'
            '    int size\n'
            'public struct Drawing\n'
            '    string name\n'
            '    List<Shape> shapes\n'
            'public int function area(Shape s)\n'
            '    match s\n'
            '        case Circle(r): return 3 * r * r\n'
            '        case Box(w, h)\n'
            '            if w < 0\n'
            '                throw ShapeError("negative", size = w)\n'
            '            return w * h\n'),
        'main.fusion': (
            'import shapes\n'
            'import shapes.Shape\n'
            'void function main()\n'
            '    shapes.Drawing d = shapes.Drawing("d", [Shape.Circle(1), Shape.Box(2, 3)])\n'
            '    shapes.Drawing copy = d\n'
            '    copy.shapes.add(Shape.Box(-1, 1))\n'
            '    int total = 0\n'
            '    for s in copy.shapes\n'
            '        int a, shapes.ShapeError err = shapes.area(s)\n'
            '        if err\n'
            '            print("{err} {err.size}")\n'
            '            continue\n'
            '        total = total + a\n'
            '    print("{total} {@1} {@2}", d.shapes.len(), copy.shapes.len())\n'),
    }) == ['negative -1', '9 2 3']


# ---------------------------------------------------------------- 27.2 the contract

def test_single_equals_compares_in_every_kind_of_condition():
    assert run_ok(main(
        'int a = 1\n'
        'int b = 1\n'
        'if a = b and b = 1 or a = 5\n'
        '    print("and/or")\n'
        'if (a = 1)\n'
        '    print("parentheses")\n'
        'if a = 2\n'
        '    print("no")\n'
        'else if a = 1\n'
        '    print("else if")\n'
        'int n = 3\n'
        'while not (n = 0)\n'
        '    n = n - 1\n'
        'print("while {n}")'
    )) == ['and/or', 'parentheses', 'else if', 'while 0']


@pytest.mark.parametrize("body", [
    'int a = 1\nbool same = a = 1',
    'int a = 1\nbool same\nsame = a = 1',
    'const int a = 1 = 1',
])
def test_single_equals_outside_a_condition_says_to_use_double(body):
    from tests.test_structs import parse
    with pytest.raises(Exception, match="'=' compares only in a condition"):
        parse(main(body))


def test_changing_a_collection_while_looping_is_an_error():
    lines, stderr = run_failing(main(
        'List<int> xs = [1, 2, 3]\n'
        'for x in xs\n'
        '    if x == 2\n'
        '        xs.removeAt(0)\n'
        '    print("{x}")'))
    assert lines == ['1', '2']
    assert 'the List changed while a for loop went over it (an element was added or removed ' \
           'inside the loop)' in stderr


def test_a_temporary_list_can_be_looped_over_without_a_check():
    c_code = generate_c('List<int> function make() : [1, 2]\n'
                        + main('for x in make()\n    print("{x}")'))
    assert 'fusion_changes_' not in c_code


# ---------------------------------------------------------------- 27.2f int to float

def analyzed(source: str, auto_widening: bool):
    from src.config import NumbersConfig
    from src.lexer import Lexer
    from src.parser.parser import Parser
    from src.semantic import SemanticAnalyzer
    analyzer = SemanticAnalyzer(numbers_config=NumbersConfig(auto_widening=auto_widening))
    ok = analyzer.analyze(Parser(Lexer(source, 'test.fusion').tokenize()).parse_program())
    return ok, '\n'.join(str(e) for e in analyzer.get_errors()), \
        '\n'.join(str(w) for w in analyzer.get_warnings())


def test_an_int_that_does_not_fit_a_float_is_an_error_by_default():
    assert run_ok(
        'float function half(float x) : x / 2.0\n'
        + main(
            'int small = 1000\n'
            'int big = 16777217\n'
            'float a = small\n'
            'print("{a} {@1}", half(small))\n'
            'List<float> values = [1.5]\n'
            'for n in [small, big]\n'
            '    try\n'
            '        values.add(n)\n'
            '        print("{@1}", n < 2.5)\n'           # compared with a float, too
            '    catch PrecisionError e\n'
            '        print("{e.kind}: {e}")\n'
            'print("{@1}", values.len())')
    ) == ['1000.000000 500.000000', 'false',
          "PrecisionError: 16777217 can't be stored exactly in a float (it would become "
          "16777216) - use a double, or set [numbers] autoWidening = true", '2']


def test_a_written_number_that_does_not_fit_is_a_compile_error():
    ok, errors, _ = analyzed(main('float f = 16777217'), auto_widening=False)
    assert not ok and "16777217 can't be stored exactly in a float" in errors
    ok, errors, _ = analyzed(main('float f = 16777216\nfloat g = 3\nprint("{f} {g}")'), auto_widening=False)
    assert ok, errors


def test_auto_widening_gives_warnings():
    ok, errors, warnings = analyzed(main('int n = 5\nfloat f = n\nfloat g = 16777217\nprint("{f} {g}")'),
                                    auto_widening=True)
    assert ok, errors
    assert "An int becomes a float here and may lose precision above 16,777,216" in warnings
    assert "16777217 can't be stored exactly in a float" in warnings


def test_int_to_double_needs_no_check():
    c_code = generate_c(main('int n = 16777217\ndouble d = n\nprint("{d}")'))
    assert 'fusion_int_to_float(' not in c_code.split('int main')[-1]


def test_numbers_section_in_fusion_toml(tmp_path):
    from src.config import load_project_config, ProjectConfigError
    source = str(tmp_path / 'p.fusion')
    assert load_project_config(source).numbers.auto_widening is False
    (tmp_path / 'fusion.toml').write_text('[numbers]\nauto_widening = true\n')
    assert load_project_config(source).numbers.auto_widening is True
    (tmp_path / 'fusion.toml').write_text('[numbers]\nauto_widening = "yes"\n')
    with pytest.raises(ProjectConfigError, match='must be true or false'):
        load_project_config(source)
