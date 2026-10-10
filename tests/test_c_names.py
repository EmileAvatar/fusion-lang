"""Tests for Task 18.4.1 (closes 15.8) - Fusion names never collide with C names.

Functions and struct types get the `fu_` prefix in C (main stays main); locals and
parameters keep their names unless the name would break the C (`auto`, `printf`,
`uint8_t`, `fusion_x`), which then get `fu_` too. Every program runs under the leak check.
"""

from tests.test_structs import generate_c, main
from tests.test_strings import run_ok


def test_functions_named_like_the_c_library():
    """A Fusion function named free, exit, abs, rename or printf used to clash with the C
    headers."""
    source = ('int function abs(int x)\n    if x < 0\n        return -x\n    return x\n\n'
              'int function free(int x) : x + 1\n\n'
              'void function exit(string why)\n    print("exit: {why}")\n\n'
              'string function rename(string s) : s + "!"\n\n'
              'int function printf(int x) : x * 2\n\n'
              + main('print("{@1} {@2} {@3} {@4}", abs(-5), free(1), rename("a"), printf(4))\n'
                     'exit("done")'))
    assert run_ok(source) == ['5 2 a! 8', 'exit: done']
    c_code = generate_c(source)
    assert 'int fu_abs(int x)' in c_code and 'int main(void)' in c_code


def test_locals_that_would_break_the_c():
    assert run_ok(main(
        'int auto = 1\n'
        'int register = 2\n'
        'int printf = 3\n'
        'string uint8_t = "u"\n'
        'int NULL = 4\n'
        'int fusion_x = 5\n'
        'int fu_y = 6\n'
        'for unsigned in range(0, 2)\n'
        '    print("{unsigned}")\n'
        'print("{auto} {register} {printf} {uint8_t} {NULL} {fusion_x} {fu_y}")'
    )) == ['0', '1', '1 2 3 u 4 5 6']


def test_parameters_that_would_break_the_c():
    assert run_ok(
        'int function add(int auto, int[] fusion_len_values)\n'
        '    return auto + len(fusion_len_values)\n\n'
        + main('int[3] v = [1, 2, 3]\nprint("{@1}", add(10, v))')) == ['13']


def test_structs_named_like_c_types():
    source = ('struct FILE\n    int size\n\nstruct size_t\n    string name\n\n'
              + main('FILE f = FILE(3)\nsize_t s = size_t("x")\nprint("{@1} {@2}", f.size, s.name)'))
    assert run_ok(source) == ['3 x']
    assert 'typedef struct fu_FILE {' in generate_c(source)


def test_plain_names_stay_readable():
    """Ordinary locals keep their names in C - only clashing ones change."""
    c_code = generate_c('int function twice(int value) : value * 2\n\n'
                        + main('int count = twice(4)'))
    assert 'int fu_twice(int value)' in c_code
    assert 'int count = fu_twice(4);' in c_code
