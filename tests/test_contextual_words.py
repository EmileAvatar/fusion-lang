"""Tests for `_` in match, `end` as a keyword, and the reserved words.

- `case Rect(w, _)`: `_` binds nothing and may be used any number of times (built in Task 25,
  documented and tested in Task 44.5)
- `End` and `end` both close a block; `end` is never a name (Task 61, D.162 - Task 44.5 had
  made a lowercase `end` an ordinary name)
- Reserved words (Task 61): kept for a planned feature or for the future - an error as a name,
  except after a `.`, where any word is a member name
"""

import pytest

from src.lexer import Lexer
from src.lexer.keywords import RESERVED_WORDS
from src.lexer.token import TokenType
from src.utils.errors import LexerError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main


def types_of(source: str, word: str) -> list:
    return [t.type for t in Lexer(source, 'test.fusion').tokenize() if t.value == word]


def test_end_is_always_a_keyword():
    assert types_of('    end function\n', 'end') == [TokenType.END]
    assert types_of('    end   if\n', 'end') == [TokenType.END]
    assert types_of('End struct\n', 'End') == [TokenType.END]
    assert types_of('int end = 3\n', 'end') == [TokenType.END]


def test_end_as_a_name_is_an_error():
    with pytest.raises(Exception):          # a parser error: `end` can't be a name
        compile_and_run(main('int end = 10\nprint("{@1}", end)'))


def test_end_function_lowercase_still_closes_a_function():
    source = ('int function twice(int x)\n'
              '    return x * 2\n'
              'end function\n\n'
              'void function main()\n'
              '    print("{@1}", twice(4))\n'
              'End function\n')
    code, out, err = compile_and_run(source)
    assert code == 0, err
    assert out.strip().splitlines()[0] == '8'


@pytest.mark.parametrize('word, kept_for', [
    ('check', 'loop safety checks'),         # a planned Fusion feature
    ('where', 'conditions on generic types'),
    ('defer', 'an idea'),
    ('type', 'future use'),                  # from other languages
    ('goto', 'future use'),
    ('default', 'future use'),
])
def test_a_reserved_word_as_a_name_says_what_it_is_kept_for(word, kept_for):
    with pytest.raises(LexerError) as info:
        Lexer(f'int {word} = 3\n', 'test.fusion').tokenize()
    assert f"'{word}' is reserved for" in str(info.value)
    assert kept_for in str(info.value)


def test_every_reserved_word_is_an_error_as_a_name():
    for word in RESERVED_WORDS:
        with pytest.raises(LexerError):
            Lexer(f'{word} = 1\n', 'test.fusion').tokenize()


def test_after_a_dot_a_reserved_word_is_a_member_name():
    tokens = Lexer('x = m.type + m.default + m.check\n', 'test.fusion').tokenize()
    names = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
    assert names == ['x', 'm', 'type', 'm', 'default', 'm', 'check']


def test_a_reserved_word_inside_a_string_or_comment_is_text():
    source = ('void function main()\n'
              '    print("type, default, goto")   // check this\n')
    code, out, err = compile_and_run(source)
    assert code == 0, err
    assert out.strip().splitlines()[0] == 'type, default, goto'


def test_underscore_skips_fields_in_match():
    source = ('enum Shape\n'
              '    Rect(int w, int h)\n'
              '    Box(int w, int h, string label)\n'
              '    Empty\n\n'
              'void function main()\n'
              '    for s in [Shape.Rect(2, 3), Shape.Box(4, 5, "b"), Shape.Empty]\n'
              '        match s\n'
              '            case Rect(w, _): print("rect {w}")\n'
              '            case Box(_, h, _): print("box {h}")\n'
              '            case Empty: print("empty")\n')
    code, out, err = compile_and_run(source)
    assert code == 0, err
    assert out.strip().splitlines()[:3] == ['rect 2', 'box 5', 'empty']
