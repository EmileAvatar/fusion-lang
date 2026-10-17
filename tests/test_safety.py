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
