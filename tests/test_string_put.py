"""Tests for Task 29.1 - changing one character of a string in place: s[i] = c.

A string is a value, so the change is to that variable's own text only: a copy made before
(`b = a`), the literal it came from, and a caller's string passed in all stay as they were.
A character of another byte width (e with an accent in place of e) moves the rest of the
text. The index is checked (an IndexError, catchable); a const string is fixed (29.2).
"""

from src.config import StructsConfig
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, errors_of


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def test_a_copy_and_the_literal_are_unchanged():
    lines = run(main('string a = "Andrew"\n'
                     'string b = a\n'
                     'b[0] = \'X\'\n'
                     'print("{a} {b}")\n'
                     'string c = "Andrew"\n'
                     'print(c)'))
    assert lines == ['Andrew Xndrew', 'Andrew']


def test_a_character_of_another_width_moves_the_rest():
    lines = run(main('string s = "caf" + "e!"\n'
                     's[3] = \'\\u00e9\'\n'
                     'print("{@1} {@2} {@3}", s, len(s), lenb(s))\n'
                     's[3] = \'e\'\n'
                     's[0] = \'\\u65e5\'\n'
                     'print("{@1} {@2} {@3}", s, len(s), lenb(s))\n'
                     'print("{@1}", s[4])'))
    assert lines == ['caf\u00e9! 5 6', '\u65e5afe! 5 7', '!']


def test_a_parameter_is_changed_only_inside_the_function():
    lines = run('void function shout(string s)\n'
                '    s[0] = \'J\'\n'
                '    print(s)\n\n'
                + main('string a = "Andrew"\n'
                       'shout(a)\n'
                       'print(a)'))
    assert lines == ['Jndrew', 'Andrew']


def test_fields_list_and_array_elements():
    lines = run('struct Person\n    string name\n\n'
                + main('Person p = Person("ann")\n'
                       'p.name[0] = \'A\'\n'
                       'List<string> xs = ["one", "two"]\n'
                       'xs[1][0] = \'T\'\n'
                       'string[2] arr = ["ab", "cd"]\n'
                       'arr[1][1] = \'D\'\n'
                       'print("{@1} {@2} {@3}", p.name, xs[1], arr[1])'))
    assert lines == ['Ann Two cD']


def test_an_index_outside_the_string_is_an_index_error():
    lines = run(main('string s = "abc"\n'
                     'try\n'
                     '    s[3] = \'z\'\n'
                     'catch IndexError e\n'
                     '    print("{e}")\n'
                     'print(s)'))
    assert 'index 3 is outside the string (length 3)' in lines[0]
    assert lines[1] == 'abc'


def test_a_const_string_is_fixed():
    message = errors_of(main('const string s = "abc"\n'
                             's[0] = \'X\''))
    assert "constant 's'" in message and 'fixed' in message


def test_the_value_must_be_a_char():
    message = errors_of(main('string s = "abc"\n'
                             's[0] = "X"'))
    assert 's[i] holds a char' in message


def test_a_returned_string_cannot_be_changed_in_place():
    message = errors_of('string function name() : "ann"\n\n'
                        + main('name()[0] = \'A\''))
    assert 'Only a stored string' in message


def test_a_fixed_string_field_when_the_project_says_so():
    message = errors_of('struct Person\n    string name\n\n'
                        + main('Person p = Person("ann")\n'
                               'p.name[0] = \'A\''),
                        StructsConfig(string_mutable=False))
    assert 'string_mutable = false' in message
