"""Tests for Task 30.0 - a statement must end its line (or its block).

`int numbers[]` used to be read silently as two statements - a plain int `numbers`, then an
empty list on its own - and `int x = 5 print(x)` as a declaration followed by a call. Both
are now errors: one statement per line. The brace style still allows `{ print(1) }` on
one line, since a `}` ends the statement.
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main


def parse(source: str):
    return Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()


@pytest.mark.parametrize('body, message', [
    ('int numbers[]', "Write the array type before the name: int[] numbers"),
    ('int x = 5 print(x)', "found 'print' - one statement per line"),
    ('string s = "a" s = "b"', "found 's' - one statement per line"),
    ('print("a") print("b")', "found 'print' - one statement per line"),
])
def test_two_statements_on_one_line_are_an_error(body, message):
    with pytest.raises(ParserError, match=message.replace('[', r'\[').replace(']', r'\]')
                       .replace('(', r'\(').replace(')', r'\)')):
        parse(main(body))


def test_a_statement_before_a_closing_brace_is_fine():
    code, out, err = compile_and_run('void function main() {\n'
                                     '    if true { print("one") }\n'
                                     '    int x = 2 }\n')
    assert code == 0, err
    assert out.strip() == 'one'
