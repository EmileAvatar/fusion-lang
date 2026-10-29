"""Tests for Task 46 - `let` / `var`, a match that gives a value, `write`.

- `let x = ...`: the type comes from the value; set once, never changes - on a struct, string,
  List or array nothing inside can change either. `let x` with no value is set exactly once
  later, on every path, before it is read
- `var x = ...`: the type comes from the value; it can change, the type can't
- `let int a` / `var int a` parameters
- Form A, a match that gives a value: `match n { 6, 7 : "Weekend", _ : "Weekday" }` - one value
  per case, every value covered, no fall through. Form B (the statement) takes `_` too
- `write(...)`: print without ending the line

With and without null checks (Rule 4b): a match value on a null enum with a `null` case gives
that case's value; without one it is a NullError, which `catch` handles.
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err                       # the leak check too
    return out.strip().splitlines()


def test_let_and_var_take_their_type_from_the_value():
    lines = run('struct Point\n    int x\n    int y\n\n'
                'int function twice(let int a, var int b)\n'
                '    b = b * 2\n'
                '    return a + b\n\n'
                + main('let greeting = "Hi"\n'
                       'var count = 0\n'
                       'count = count + 2\n'
                       'let p = Point(1, 2)\n'
                       'var price = 2.5\n'
                       'price = price * 2.0\n'
                       'print("{greeting} {count} {p.y} {@1} {@2}", price, twice(1, 2))'))
    assert lines == ['Hi 2 2 5.000000 5']


def test_a_let_set_later_on_every_path():
    lines = run(main('int count = 3\n'
                     'let total\n'
                     'if count > 1\n'
                     '    total = 100\n'
                     'else\n'
                     '    total = 1\n'
                     'var later\n'
                     'later = "a"\n'
                     'later = later + "b"\n'
                     'print("{total} {later}")'))
    assert lines == ['100 ab']


def test_module_level_let_and_var():
    lines = run('let LIMIT = 3\nlet NAME = "box"\n\n' + main('print("{NAME} {LIMIT}")'))
    assert lines == ['box 3']


def test_match_gives_a_value():
    lines = run('enum Light: Red Yellow Green\n\n'
                'string function name(int n) : "n{n}"\n\n'
                'string function day(int n)\n'
                '    return match n { 6, 7 : "Weekend", _ : "Weekday" }\n\n'
                + main('int count = 5\n'
                       'string size = match count\n'
                       '    0 : "none"\n'
                       '    1, 2, 3 : "few"\n'
                       '    else : name(count)\n'
                       'print(size)\n'
                       'print(day(6))\n'
                       'print(day(2))\n'
                       'Light l = Light.Green\n'
                       'let action = match l { Red, Yellow : "stop", Green : "go" }\n'
                       'print(action)\n'
                       'int n = match \'x\' { \'x\' : 1, _ : 2 }\n'
                       'print("{n}")'))
    assert lines == ['n5', 'Weekend', 'Weekday', 'go', '1']


def test_a_null_enum_with_and_without_a_null_case():
    lines = run('enum Light: Red Yellow Green\n\n'
                + main('Light none\n'
                       'let safe = match none { null : "no light", _ : "a light" }\n'
                       'print(safe)\n'
                       'try\n'
                       '    string bad = match none { Red : "r", Yellow : "y", Green : "g" }\n'
                       '    print(bad)\n'
                       'catch err\n'
                       '    print("caught: {err.message}")'))
    assert lines == ['no light', 'caught: a match on a null Light with no case for null']


def test_a_match_statement_takes_an_underscore():
    lines = run(main('for n in range(1, 4)\n'
                     '    match n\n'
                     '        case 1: print("one")\n'
                     '        case _: print("other")\n'
                     'match 9\n'
                     '    case 2, 4, 6: print("even")\n'
                     '    _: print("else")'))
    assert lines == ['one', 'other', 'other', 'else']


def test_write_does_not_end_the_line():
    lines = run(main('write("Name: ")\nwrite("{@1}+{@2}=", 1, 2)\nprint("3")'))
    assert lines == ['Name: 1+2=3']


@pytest.mark.parametrize('code, message', [
    ('let a = 1\na = 2', "'a' is a let - it can't change once set"),
    ('let s = "abc"\ns[0] = \'x\'', "Cannot change a character of constant 's'"),
    ('let xs = [1, 2]\nxs[0] = 9', "Cannot assign to element of constant array 'xs'"),
    ('var v = 1\nv = "text"', "Cannot assign string to variable of type int"),
    ('let n = null', "'let n' takes its type from its value: null has no type"),
    ('let e = []', "'let e' takes its type from its value: [] has no element type"),
    ('let t\nprint("{t}")', "'t' is read before it has a value"),
    ('let u\nu = 1\nu = 2', "'u' is a let - it can be set only once"),
    ('let w\nfor i in range(0, 3)\n    w = i', "setting it inside a loop would set it more"),
    ('var v\nif true\n    v = 1\nprint("{v}")', "'v' is read before it has a value"),
    ('int k = match 1 { 1 : 10, 2 : "two", _ : 0 }', "Every case of a match that gives a value "
                                                     "gives the same type"),
    ('int j = match 1 { 1 : 10 }', "A match on int needs an else (or _)"),
])
def test_usage_errors(code, message):
    assert message in errors_of(main(code))


@pytest.mark.parametrize('source, message', [
    ('struct P\n    int x\n\nvoid function main()\n    let p = P(1)\n    p.x = 5\n',
     "Cannot assign to field 'x' of constant 'p'"),
    ('void function f(let int a)\n    a = 2\n\nvoid function main()\n    f(1)\n',
     "'a' is a let parameter - it can't change in the function"),
    ('enum Light: Red Yellow Green\n\nvoid function main()\n    Light l\n'
     '    string m = match l { Red : "r", Yellow : "y" }\n',
     "doesn't handle Green - add a case for it, or an else (or _)"),
    ('let x\n\nvoid function main()\n    print("a")\n', "A module-level 'let x' needs its value"),
])
def test_declaration_errors(source, message):
    assert message in errors_of(source)


@pytest.mark.parametrize('code, message', [
    ('let int x = 5', "'let' takes its type from the value"),
    ('string s = match 1 { case 1 : "a" }', "A match that gives a value has no 'case'"),
    ('string s = fall match 1 { 1 : "a" }', "A match that gives a value can't fall through"),
    ('string s = match 1 { 1 : print("a") print("b") }', "A case of a match value is one value"),
    ('match 1\n    1: print("a")', "Each part of a match statement starts with 'case'"),
])
def test_parse_errors(code, message):
    with pytest.raises(ParserError, match=message.replace('(', r'\(').replace(')', r'\)')):
        Parser(Lexer(main(code), 't').tokenize()).parse_program()


def test_a_parameter_needs_its_type():
    with pytest.raises(ParserError, match="Give the parameter's type: let int a"):
        Parser(Lexer('void function f(let a)\n    print("x")\n', 't').tokenize()).parse_program()
