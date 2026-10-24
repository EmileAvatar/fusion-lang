"""Tests for Task 28.1.5 - \\{ and \\} escapes: a literal brace in a string or char.

A `{` on its own starts an interpolation; `\\{` is the brace as text. Found while planning
the self-hosted compiler, which writes C full of braces.
"""

from src.lexer import Lexer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main


def run(body: str) -> str:
    code, out, err = compile_and_run(main(body))
    assert code == 0, err
    return out


def test_escaped_braces_are_text():
    assert run('print("int main() \\{ return 0; \\}")').strip() == 'int main() { return 0; }'


def test_escaped_braces_next_to_an_interpolation():
    assert run('string name = "Ada"\nprint("\\{name\\} is {name}")').strip() == '{name} is Ada'


def test_escaped_braces_in_a_string_value_and_format():
    out = run('string s = "\\{" + "x" + "\\}"\n'
              'string f = format("\\{@1\\} = {@1}", 7)\n'
              'print(s + " " + f)')
    assert out.strip() == '{x} {@1} = 7'


def test_a_brace_as_a_char():
    assert run("char c = '\\{'\nprint(\"{c}\")").strip() == '{'


def test_a_lone_brace_is_still_an_error():
    lexer = Lexer('void function main()\n    print("{ ")\n', 'test.fusion')
    try:
        lexer.tokenize()
    except Exception as e:                       # the lexer stops at the bad interpolation
        assert 'interpolation' in str(e)
        return
    assert lexer.diagnostics.errors              # or reports it as an error
