"""Tests for Task 44.3 - a line break inside ( or [ continues the line.

Inside parentheses and brackets the lexer makes no NEWLINE, INDENT or DEDENT, so a long call
or list literal can be written over several lines. Braces still open blocks.
"""

from src.lexer import Lexer
from src.lexer.token import TokenType
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main


def kinds(source: str) -> list:
    return [t.type for t in Lexer(source, 'test.fusion').tokenize()]


def test_no_newline_or_indent_inside_parentheses():
    types = kinds('print("{@1} {@2}",\n      1,\n      2)\n')
    assert TokenType.NEWLINE in types
    assert types.count(TokenType.NEWLINE) == 1           # only the one after ')'
    assert TokenType.INDENT not in types and TokenType.DEDENT not in types


def test_no_newline_inside_brackets_or_nested():
    types = kinds('x = [1,\n  [2,\n   3],\n  4]\n')
    assert types.count(TokenType.NEWLINE) == 1


def test_lines_and_columns_still_count_inside_the_brackets():
    tokens = Lexer('f(1,\n  22)\n', 'test.fusion').tokenize()
    number = [t for t in tokens if t.value == '22'][0]
    assert (number.location.line, number.location.column) == (2, 3)


def test_a_long_call_and_list_over_several_lines():
    body = ('List<int> numbers = [1,\n'
            '                     2,\n'
            '                     3]\n'
            'print("{@1} {@2} {@3}",\n'
            '      numbers.len(),\n'
            '      numbers[0],\n'
            '      numbers[2])\n'
            'if numbers.len() == 3\n'
            '    print("still indented")\n')
    code, out, err = compile_and_run(main(body))
    assert code == 0, err
    assert out.split('\n')[:2] == ['3 1 3', 'still indented']


def test_a_closing_bracket_with_nothing_open_is_still_an_error():
    import pytest
    from src.parser.parser import Parser, ParserError
    tokens = Lexer(main('int x = 1)\nprint("{x}")'), 'test.fusion').tokenize()
    with pytest.raises(ParserError):
        Parser(tokens).parse_program()


def test_an_unclosed_bracket_is_an_error_not_a_swallowed_program():
    import pytest
    from src.parser.parser import Parser, ParserError
    tokens = Lexer(main('print("{@1}", (1\nprint("never")'), 'test.fusion').tokenize()
    with pytest.raises(ParserError):
        Parser(tokens).parse_program()
