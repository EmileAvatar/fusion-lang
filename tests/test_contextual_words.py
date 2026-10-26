"""Tests for Task 44.5 - `_` in match, and `end` / `var` as ordinary names.

- `case Rect(w, _)`: `_` binds nothing and may be used any number of times (built in Task 25,
  documented and tested here)
- `End` closes a block; a lowercase `end` does only right before a block word (`end
  function`) and is an ordinary name everywhere else
- `var` is an ordinary name until type inference exists
"""

from src.lexer import Lexer
from src.lexer.token import TokenType
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main


def types_of(source: str, word: str) -> list:
    return [t.type for t in Lexer(source, 'test.fusion').tokenize() if t.value == word]


def test_end_closes_a_block_only_before_a_block_word():
    assert types_of('int end = 3\n', 'end') == [TokenType.IDENTIFIER]
    assert types_of('    end function\n', 'end') == [TokenType.END]
    assert types_of('    end   if\n', 'end') == [TokenType.END]
    assert types_of('End struct\n', 'End') == [TokenType.END]


def test_end_and_var_as_names_in_a_program():
    body = ('int end = 10\n'
            'int var = 5\n'
            'print("{@1}", end - var)')
    code, out, err = compile_and_run(main(body))
    assert code == 0, err
    assert out.strip().splitlines()[0] == '5'


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
