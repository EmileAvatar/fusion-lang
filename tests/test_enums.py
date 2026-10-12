"""Tests for Task 25.2 - plain enums.

`enum Color: Red Green Blue` (or an indented / braced / End-keyword block; commas
optional), explicit values (`OK = 200`), `Color.Red`, == / != within one enum, printing the
name, toString / toInt, Color.values(), Color.fromString(text), and enums as variables,
parameters, return values, struct fields, array / List elements and Map keys, across
modules too. Every program runs under the leak check.
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser
from src.parser.ast_nodes import EnumDecl
from tests.test_structs import errors_of, generate_c, main
from tests.test_strings import run_ok, run_error
from tests.test_modules import errors as module_errors, run_project


def parse(source: str):
    return Parser(Lexer(source, 'test').tokenize()).parse_program()


def enum_of(source: str) -> EnumDecl:
    return next(d for d in parse(source).declarations if isinstance(d, EnumDecl))


# ---------------------------------------------------------------- parsing

@pytest.mark.parametrize("source", [
    'enum Color: Red Green Blue\n',
    'enum Color: Red, Green, Blue\n',
    'enum Color\n    Red\n    Green\n    Blue\n',
    'enum Color\n    Red, Green\n    Blue\n',
    'enum Color {\n    Red,\n    Green,\n    Blue\n}\n',
    'enum Color { Red Green Blue }\n',
    'enum Color\n    Red\n    Green\n    Blue\nEnd enum\n',
    'Enum Color: Red Green Blue\n',
])
def test_every_form_parses_to_the_same_enum(source):
    enum = enum_of(source + 'void function main()\n    print("x")\n')
    assert enum.name == 'Color'
    assert [(v.name, v.value) for v in enum.variants] == [('Red', 0), ('Green', 1), ('Blue', 2)]


def test_values_count_on_from_the_last_given_one():
    enum = enum_of('enum Status\n    OK = 200\n    Created\n    NotFound = 404\n    Low = -1\n    Next\n')
    assert [(v.name, v.value, v.explicit_value) for v in enum.variants] == [
        ('OK', 200, True), ('Created', 201, False), ('NotFound', 404, True),
        ('Low', -1, True), ('Next', 0, False)]


def test_public_enum():
    assert enum_of('public enum Color: Red\n').is_public


@pytest.mark.parametrize("source, message", [
    ('enum Color:\n', "has no values"),
    ('enum Color\nvoid function main()\n    print("x")\n', "Expected the values of enum"),
    ('enum Status\n    OK = "x"\n', "must be a whole number"),
])
def test_parse_errors(source, message):
    with pytest.raises(Exception, match=message):
        parse(source)


# ---------------------------------------------------------------- running

def test_values_print_compare_convert():
    assert run_ok(
        'enum Color: Red Green Blue\n'
        'enum Status\n    OK = 200\n    NotFound = 404\n'
        + main(
            'Color c = Color.Green\n'
            'print("{c} {@1} {@2} {@3}", c.toInt(), toInt(Status.NotFound), Status.OK)\n'
            'print(toString(c) + "!" + c.toString())\n'
            'print("{@1} {@2} {@3}", c == Color.Green, c != Color.Red, c === Color.Green)\n'
            'string text = "{c}"\n'
            'print(text)')
    ) == ['Green 1 404 OK', 'Green!Green', 'true true true', 'Green']


def test_parameters_return_values_and_defaults():
    assert run_ok(
        'enum Light: Red Yellow Green\n'
        'enum Status\n    OK = 200\n    Fail = 500\n'
        'struct Lamp\n    string name\n    Status status\n    Light light = Light.Yellow\n'
        'Light function next(Light l)\n'
        '    if l == Light.Red\n'
        '        return Light.Green\n'
        '    if l == Light.Green\n'
        '        return Light.Yellow\n'
        '    return Light.Red\n'
        + main(
            'Light l\n'                                    # no value given: the first one
            'Status s\n'
            'Lamp lamp = Lamp("hall", Status.Fail)\n'
            'Status[2] codes\n'
            'print("{l} {s} {@1} {@2} {@3} {@4}", lamp.light, lamp.status, codes[1], next(next(l)))\n'
            'lamp.light = next(lamp.light)\n'
            'print("{@1}", lamp.light)')
    ) == ['Red OK Yellow Fail OK Yellow', 'Red']


def test_values_from_string_lists_and_maps():
    assert run_ok(
        'enum Color: Red Green Blue\n'
        + main(
            'for c in Color.values()\n'
            '    print("{c}")\n'
            'List<Color> picked = [Color.Blue, Color.Red]\n'
            'picked.add(Color.fromString("Green"))\n'
            'Map<Color, int> counts\n'
            'for c in picked\n'
            '    counts[c] = counts.get(c, 0) + 1\n'
            'counts[Color.Red] = counts[Color.Red] + 5\n'
            'print("{@1} {@2} {@3} {@4}", picked.len(), picked[2], counts[Color.Red], picked == [Color.Blue, Color.Red, Color.Green])\n'
            'for c in counts\n'
            '    print("{c}={@1}", counts[c])')
    ) == ['Red', 'Green', 'Blue', '3 Green 6 true', 'Blue=1', 'Red=6', 'Green=1']


def test_a_stored_values_list_is_freed_once():
    assert run_ok(
        'enum Color: Red Green Blue\n'
        + main(
            'List<Color> all = Color.values()\n'
            'all = Color.values()\n'
            'all.removeAt(0)\n'
            'print("{@1} {@2}", all.len(), Color.values().len())')
    ) == ['2 3']


def test_from_string_of_an_unknown_name_stops_the_program():
    stderr = run_error('enum Color: Red Green\n' + main('Color c = Color.fromString("Pink")\nprint("{c}")'))
    assert '"Pink" is not a value of enum Color' in stderr


def test_missing_map_key_names_the_value():
    stderr = run_error('enum Color: Red Green\n' + main('Map<Color, int> m\nprint("{@1}", m[Color.Green])'))
    assert 'key Green is not in the map' in stderr


def test_c_code_is_an_int_with_helpers():
    c_code = generate_c('enum Color: Red Green\n' + main('Color c = Color.Green\nprint("{c}")'))
    assert 'typedef int fu_Color;' in c_code
    assert 'fu_Color c = 1;' in c_code
    assert 'fu_Color__text(c).data' in c_code


# ---------------------------------------------------------------- errors

@pytest.mark.parametrize("body, message", [
    ('Color c = Color.Pink', "Enum 'Color' has no value 'Pink' (its values: Red, Green)"),
    ('Color c = 1', "Cannot assign int to variable of type Color"),
    ('int n = Color.Red', "Cannot assign Color to variable of type int"),
    ('bool b = Color.Red == 0', "an enum value only equals a value of the same enum"),
    ('bool b = Color.Red == Size.Big', "an enum value only equals a value of the same enum"),
    ('int n = Color.Red + 1', "Color"),
    ('Color c = Color.Red()', "'Color.Red' is a value, not a function"),
    ('Color c = Color.first()', "Enum 'Color' has no function 'first'"),
    ('List<Color> cs = Color.values(1)', "Color.values() takes 0 argument(s), got 1"),
    ('Color c = Color.fromString(1)', "Color.fromString() needs string, got int"),
    ('string s = Color.Red.toUpper()', "An enum value has no method 'toUpper'"),
    ('int Color = 1', "'Color' is an enum - choose another name for the variable"),
])
def test_type_errors(body, message):
    assert message in errors_of('enum Color: Red Green\nenum Size: Big Small\n' + main(body))


@pytest.mark.parametrize("source, message", [
    ('enum Color: Red Red\n', "Enum 'Color' has two values named 'Red'"),
    ('enum Status\n    OK = 1\n    Fine = 1\n', "'Fine' and 'OK' in enum 'Status' both have the value 1"),
    ('enum Color: Red values\n', "'values' can't be a value of enum 'Color'"),
    ('enum List: A B\n', "'List' is a built-in type"),
    ('enum Color: Red\nstruct Color\n    int x\n', "Color"),
])
def test_declaration_errors(source, message):
    assert message in errors_of(source + main('print("x")'))


# ---------------------------------------------------------------- modules

def test_enums_across_modules(tmp_path):
    assert run_project(tmp_path, {
        'paint/colors.fusion': (
            'public enum Color: Red Green Blue\n'
            'public Color function warm()\n'
            '    return Color.Red\n'),
        'main.fusion': (
            'import paint\n'
            'import paint.Color\n'
            'void function main()\n'
            '    paint.Color a = paint.warm()\n'
            '    Color b = Color.Blue\n'
            '    print("{a} {b} {@1}", paint.Color.Green)\n'),
    }) == ['Red Blue Green']


def test_a_private_enum_stays_in_its_module(tmp_path):
    message = module_errors(tmp_path, {
        'paint/colors.fusion': (
            'enum Secret: A B\n'
            'public Secret function hidden()\n'
            '    return Secret.A\n'),
        'main.fusion': 'import paint\nvoid function main()\n    print("x")\n',
    })
    assert "The public function 'hidden' uses the private enum 'Secret'" in message


# ---------------------------------------------------------------- match (Task 25.3)

LIGHT = 'enum Light: Red Yellow Green\n'


def test_match_on_an_enum_in_every_block_style():
    assert run_ok(
        LIGHT
        + 'string function action(Light l)\n'
        '    match l\n'
        '        case Red, Yellow\n'
        '            return "stop"\n'
        '        case Green: return "go"\n'
        + 'string function braces(Light l) {\n'
        '    match l {\n'
        '        case Green {\n'
        '            return "go"\n'
        '        }\n'
        '        else: return "wait"\n'
        '    }\n'
        '}\n'
        + 'string function ended(Light l)\n'
        '    string text = "?"\n'
        '    match l\n'
        '        case Red: text = "R"\n'
        '        case Yellow: text = "Y"\n'
        '        case Green: text = "G"\n'
        '    End match\n'
        '    return text\n'
        + main(
            'for l in Light.values()\n'
            '    print("{l} {@1} {@2} {@3}", action(l), braces(l), ended(l))')
    ) == ['Red stop wait R', 'Yellow stop wait Y', 'Green go go G']


def test_match_on_int_char_and_string():
    assert run_ok(main(
        'for n in [0, 1, -1, 7]\n'
        '    match n\n'
        '        case 0: print("zero")\n'
        '        case 1, 2: print("small")\n'
        '        case -1: print("minus one")\n'
        '        else: print("other {n}")\n'
        'for ch in [\'+\', \'x\']\n'
        '    match ch\n'
        '        case \'+\', \'-\': print("operator")\n'
        '        else: print("letter")\n'
        'for word in split("go stop", " ")\n'
        '    match word\n'
        '        case "go": print("moving")\n'
        '        else: print("halt")'
    )) == ['zero', 'small', 'minus one', 'other 7', 'operator', 'letter', 'moving', 'halt']


def test_break_and_continue_in_a_case_act_on_the_loop():
    assert run_ok(main(
        'for n in range(0, 10)\n'
        '    match n\n'
        '        case 1: continue\n'
        '        case 4: break\n'
        '        else: print("{n}")'
    )) == ['0', '2', '3']


def test_a_temporary_string_subject_is_freed():
    assert run_ok(main(
        'string name = "Ada"\n'
        'match name + "!"\n'
        '    case "Ada!": print("hi " + name)\n'
        '    else: print("who")'
    )) == ['hi Ada']


def test_a_match_that_always_returns_needs_no_return_after_it():
    assert run_ok(
        LIGHT + 'int function code(Light l)\n'
        '    match l\n'
        '        case Red: return 1\n'
        '        case Yellow: return 2\n'
        '        case Green: return 3\n'
        + main('print("{@1}", code(Light.Green))')
    ) == ['3']


@pytest.mark.parametrize("body, message", [
    ('match l\n    case Red: print("r")',
     "This match on Light doesn't handle Yellow, Green - add a case for them, or an else"),
    ('match l\n    case Red, Red: print("r")\n    else: print("x")', "'Red' is already handled by an earlier case"),
    ('match l\n    case Pink: print("p")\n    else: print("x")', "Enum 'Light' has no value 'Pink'"),
    ('match l\n    case 1: print("p")\n    else: print("x")', "A case on enum 'Light' names one of its values"),
    ('match l\n    case Red(x): print("p")\n    else: print("x")', "'Red' carries no data"),
    ('match 5\n    case 1: print("one")', "A match on int needs an else"),
    ('match 5\n    case 1, 1: print("one")\n    else: print("x")', "This value is already handled"),
    ('match 5\n    case "a": print("a")\n    else: print("x")', "This case is string, but the match is on int"),
    ('int k = 1\nmatch 5\n    case k: print("a")\n    else: print("x")', "A case on int needs a constant"),
    ('match 2.5\n    case 1: print("a")\n    else: print("x")', "match works on an enum, int, byte, char or string value, got float"),
])
def test_match_errors(body, message):
    assert message in errors_of(LIGHT + main('Light l = Light.Red\n' + body))


def test_an_else_after_every_value_is_a_warning():
    from tests.test_structs import warnings_of
    assert "The else of this match never runs" in warnings_of(LIGHT + main(
        'Light l = Light.Red\n'
        'match l\n'
        '    case Red, Yellow, Green: print("all")\n'
        '    else: print("never")'))


def test_a_match_without_every_case_returning_needs_a_return():
    assert "return" in errors_of(
        LIGHT + 'int function code(Light l)\n'
        '    match l\n'
        '        case Red: return 1\n'
        '        else: print("no")\n' + main('print("x")'))


@pytest.mark.parametrize("source, message", [
    ('match 1\n', "Expected the cases of 'match'"),
    ('match 1\n    else: print("x")\n    case 1: print("y")\n', "'else' must be the last part"),
    ('match l\n    case Light.Red: print("x")\n', "In a case, write just the value's name: case Red"),
    ('match l\n    case Red print("x")\n', "Expected the body of the case"),
])
def test_match_parse_errors(source, message):
    with pytest.raises(Exception, match=message):
        parse(LIGHT + main(source))


# ---------------------------------------------------------------- enums with data (Task 25.4)

TOKEN = ('enum Token\n'
         '    Number(int value)\n'
         '    Word(string text)\n'
         '    Pair(string a, int b)\n'
         '    Plus\n')


def test_data_values_are_made_and_read_through_match():
    assert run_ok(
        TOKEN
        + 'string function show(Token t)\n'
        '    match t\n'
        '        case Number(n): return "number " + toString(n)\n'
        '        case Word(w): return "word " + w\n'
        '        case Pair(x, _): return "pair " + x\n'
        '        case Plus: return "plus"\n'
        + main(
            'List<Token> tokens = [Token.Number(42), Token.Word("hi"), Token.Plus]\n'
            'tokens.add(Token.Pair(b = 7, a = "k"))\n'
            'for t in tokens\n'
            '    print("{t} {@1} {@2}", toInt(t), show(t))')
    ) == ['Number 0 number 42', 'Word 1 word hi', 'Plus 3 plus', 'Pair 2 pair k']


def test_data_values_are_copied_compared_and_freed():
    assert run_ok(
        TOKEN + 'struct Slot\n    Token token\n    int n\n'
        + 'Token function word(string s)\n    return Token.Word(s + "!")\n'
        + main(
            'Token a = word("x")\n'
            'Token b = a\n'
            'a = Token.Number(1)\n'
            'Slot slot = Slot(b, 2)\n'
            'Token none\n'                          # no value given: the first value, Number(0)
            'print("{@1} {@2} {@3}", b == Token.Word("x!"), a == b, a != Token.Number(2))\n'
            'print("{@1} {@2} {none}", slot.token == b, none == Token.Number(0))\n'
            'match word("y")\n'
            '    case Word(w): print(w)\n'
            '    else: print("?")')
    ) == ['true false true', 'true true Number', 'y!']


def test_a_return_inside_a_case_frees_the_matched_value():
    assert run_ok(
        TOKEN + 'string function first(List<Token> ts)\n'
        '    for t in ts\n'
        '        match t\n'
        '            case Word(w)\n'
        '                if w == "stop"\n'
        '                    return w\n'
        '            else: continue\n'
        '    return "none"\n'
        + 'Token function make(string s)\n    return Token.Word(s)\n'
        + 'string function direct(string s)\n'
        '    match make(s)\n'
        '        case Word(w): return w + "?"\n'
        '        else: return "-"\n'
        + main('print(first([Token.Plus, Token.Word("go"), Token.Word("stop")]) + " " + direct("q"))')
    ) == ['stop q?']


def test_binding_names_that_clash_with_c_are_renamed():
    assert run_ok(TOKEN + main(
        'Token t = Token.Number(5)\n'
        'match t\n'
        '    case Number(auto): print("{auto}")\n'
        '    else: print("x")'
    )) == ['5']


@pytest.mark.parametrize("body, message", [
    ('Token t = Token.Number()', "'Token.Number' takes 1 value(s) (value), got 0"),
    ('Token t = Token.Number("x")', "'Token.Number' field 'value': expected int, got string"),
    ('Token t = Token.Number', "'Token.Number' carries data - give it: Token.Number(value)"),
    ('Token t = Token.Plus()', "'Token.Plus' is a value, not a function"),
    ('Token t = Token.Pair(c = 1)', "has no field named 'c'"),
    ('List<Token> ts = Token.values()', "Token.values() only works on an enum whose values carry no data"),
    ('Map<Token, int> m', "Map keys can be string, int, char or an enum without data"),
    ('Token t = Token.Plus\nmatch t\n    case Number(a, b): print("x")\n    else: print("y")',
     "'Number' carries 1 value(s) (value) - name each, or write just case Number"),
    ('Token t = Token.Plus\nmatch t\n    case Number(a), Word(b): print("x")\n    else: print("y")',
     "A case with several values can't name their data"),
    ('Token t = Token.Plus\nmatch t\n    case Number(n): n = "x"\n    else: print("y")', "Cannot assign"),
])
def test_data_errors(body, message):
    assert message in errors_of(TOKEN + main(body))


@pytest.mark.parametrize("source, message", [
    ('enum E\n    A(int x, int x)\n', "'A' of enum 'E' has two fields named 'x'"),
    ('enum E\n    A(int x = 1)\n', "can't have a default value"),
    ('enum E\n    A(int[3] x)\n', "can't be an array - use a List"),
    ('enum E\n    A(E inner)\n', "enums that hold themselves come in Task 25.5"),
])
def test_data_declaration_errors(source, message):
    assert message in errors_of(source + main('print("x")'))
