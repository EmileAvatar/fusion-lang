"""Tests for Task 26 - error handling.

26.2: the `Error` value (message, code, where), functions that can fail (`T, Error
function`, `Error function`, `return Error(...)`), capturing an error from any call
(`T x, Error err = f()`, `Error e = f()`), `if err`, and errors nobody captures bubbling up
to main, where the program stops with the message. Every program runs under the leak
check, so every path an error takes must free what it holds.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import errors_of, generate_c, main
from tests.test_strings import run_ok

SHIP = ('struct Ship\n    string name\n    int crew\n'
        'Ship, Error function loadShip(string name)\n'
        '    if name == ""\n'
        '        return Error("No name given", 400)\n'
        '    if name == "x"\n'
        '        return Error("Bad ship {name}")\n'
        '    return Ship(name + "!", 3)\n')


def run_failing(source: str) -> tuple:
    """A program expected to stop with an error nobody caught: (stdout lines, stderr)."""
    exit_code, stdout, stderr = compile_and_run(source)
    assert exit_code == 1, f"expected exit 1, got {exit_code}: {stdout}{stderr}"
    return stdout.splitlines(), stderr


# ---------------------------------------------------------------- 26.2 Error and error returns

def test_capture_an_error_and_its_fields():
    assert run_ok(SHIP + main(
        'Ship s, Error err = loadShip("")\n'
        'if err\n'
        '    print("{err} / {@1} / {@2} / [{s.name}]", err.code, err.where)\n'
        'Ship t, Error none = loadShip("Dawn")\n'
        'print("{t.name} {@1} {@2} {@3} [{none}]", not none, none.code, none.message == "")\n'
        'Ship u, Error e2 = loadShip("x")\n'
        'print("{e2} {@1}", e2.code)'
    )) == ['No name given / 400 / test.fusion:6 / []', 'Dawn! true 0 true []', 'Bad ship x 0']


def test_a_void_function_that_can_fail_and_capture_only():
    assert run_ok(
        'Error function save(string name)\n'
        '    if name == ""\n'
        '        return Error("nothing to save")\n'
        '    print("saved " + name)\n'
        + main(
            'Error a = save("log")\n'
            'Error b = save("")\n'
            'print("{@1} {@2} {b}", not a, b and true)\n'
            'Error made = Error("just a value", 7)\n'
            'print("{made} {@1}", made.code)')
    ) == ['saved log', 'true true nothing to save', 'just a value 7']


def test_an_error_bubbles_up_and_everything_is_freed():
    assert run_ok(SHIP
        + 'string function describe(string name)\n'       # can't fail itself - passes it on
        '    string text = "ship: " + name\n'
        '    List<string> parts = ["a", "b", text]\n'
        '    Ship s = loadShip(name)\n'
        '    return text + s.name + parts[2]\n'
        + 'string, Error function outer(string name)\n'
        '    string r = describe(name) + "?"\n'
        '    return r\n'
        + main(
            'string ok, Error e1 = outer("Dawn")\n'
            'print(ok)\n'
            'string bad, Error e2 = outer("")\n'
            'print("[{bad}] {e2}")')
    ) == ['ship: DawnDawn!ship: Dawn?', '[] No name given']


def test_an_error_nobody_captures_stops_the_program():
    lines, stderr = run_failing(SHIP + main(
        'string keep = "held"\n'
        'Ship s = loadShip("Dawn")\n'
        'print(s.name + keep)\n'
        'Ship t = loadShip("x")\n'
        'print("never")'
    ))
    assert lines == ['Dawn!held']
    assert 'Error at test.fusion:8: Bad ship x' in stderr


def test_passing_an_error_on_with_return_err():
    assert run_ok(SHIP
        + 'int, Error function crewOf(string name)\n'
        '    Ship s, Error err = loadShip(name)\n'
        '    if err\n'
        '        return err\n'
        '    return s.crew\n'
        + main(
            'int a, Error e1 = crewOf("Dawn")\n'
            'int b, Error e2 = crewOf("")\n'
            'print("{a} {@1} {b} {e2}", not e1)')
    ) == ['3 true 0 No name given']


def test_capture_in_a_loop_and_in_expressions():
    assert run_ok(SHIP + main(
        'for name in ["A", "", "B", "x"]\n'
        '    string text, Error err = loadShip(name).name + "/" + loadShip("C").name\n'
        '    if err\n'
        '        print("error: " + err.message)\n'
        '        continue\n'
        '    print(text)'
    )) == ['A!/C!', 'error: No name given', 'B!/C!', 'error: Bad ship x']


def test_calls_through_function_values_and_lambdas_pass_errors_on():
    assert run_ok(
        'int, Error function half(int n)\n'
        '    if n % 2 == 1\n'
        '        return Error("odd: {n}")\n'
        '    return n / 2\n'
        + main(
            '(int) : int f = half\n'
            'int a, Error e1 = f(8)\n'
            'int b, Error e2 = f(3)\n'
            '(int) : int g = func(int x) : half(x) + 1\n'
            'int c, Error e3 = g(5)\n'
            'print("{a} {b} {e2} {c} {e3}")')
    ) == ['4 0 odd: 3 0 odd: 5']


def test_a_match_on_a_failing_call():
    assert run_ok(SHIP + main(
        'string r, Error err = describe("")\n'
        'print("[{r}] {err}")'
    ).replace('void function main()', 'string, Error function describe(string n)\n'
              '    match loadShip(n).crew\n'
              '        case 3: return "three"\n'
              '        else: return "other"\n'
              'void function main()')) == ['[] No name given']


def test_programs_without_errors_get_no_checks():
    c_code = generate_c('int function twice(int n) : n * 2\n' + main(
        '(int) : int f = twice\nprint("{@1}", f(2) + twice(3))'))
    assert 'fusion_failed) goto' not in c_code


@pytest.mark.parametrize("source, message", [
    ('int function f()\n    return Error("x")\n', "This function can't fail - declare it 'T, Error function'"),
    ('Error, Error function f()\n    return Error("x")\n', "a function that can fail is 'T, Error function'"),
    ('void function f()\n    Error e = Error(1)\n', "Error(...) needs a string message, got int"),
    ('void function f()\n    Error e = Error("a", "b")\n', "Error(...) needs a int code, got string"),
    ('void function f()\n    Error e = Error()\n', "Error(...) takes a message and optionally a code"),
    ('void function f()\n    Error e = Error("a")\n    print(e.text)\n', "An Error has no field 'text'"),
    ('struct Error\n    int x\n', "'Error' is a built-in type"),
    ('void function f()\n    Error e = Error("a")\n    int n = e + 1\n', "Error"),
])
def test_error_type_errors(source, message):
    assert message in errors_of(source + main('print("x")'))


@pytest.mark.parametrize("source, message", [
    (main('int n, string s = 1'), "After ',' a declaration names the variable that captures the error"),
    (main('int n, Error e'), "needs a call to capture"),
])
def test_capture_parse_errors(source, message):
    with pytest.raises(Exception, match=message):
        errors_of(source)


# ---------------------------------------------------------------- 26.3 try / catch / finally / throw

HALF = ('int, Error function half(int n)\n'
        '    if n % 2 == 1\n'
        '        return Error("odd: {n}", 7)\n'
        '    return n / 2\n'
        'int function strict(int n)\n'
        '    if n < 0\n'
        '        throw Error("negative")\n'
        '    return n\n')


def test_try_catch_finally_in_a_loop_with_break_and_continue():
    assert run_ok(HALF
        + 'string function walk()\n'
        '    string log = ""\n'
        '    for n in [4, 3, -2, 8, 6]\n'
        '        try\n'
        '            string note = "n" + toString(n)\n'
        '            int h = half(strict(n))\n'
        '            log = log + note + "=" + toString(h) + " "\n'
        '            if h == 4\n'
        '                break\n'
        '        catch err\n'
        '            log = log + "[" + err.message + "] "\n'
        '            if err.code == 0\n'
        '                continue\n'
        '            log = log + "code " + toString(err.code) + " "\n'
        '        finally\n'
        '            log = log + "f "\n'
        '    return log\n'
        + main('print(walk())')
    ) == ['n4=2 f [odd: 3] code 7 f [negative] f n8=4 f ']


def test_finally_runs_before_return_and_when_an_error_passes():
    assert run_ok(HALF
        + 'int function early(int n)\n'
        '    string held = "x" + toString(n)\n'
        '    try\n'
        '        return half(n)\n'
        '    finally\n'
        '        print("finally " + held)\n'
        + main(
            'print("{@1}", early(10))\n'
            'int r, Error err = early(3)\n'
            'print("{r} {err}")')
    ) == ['finally x10', '5', 'finally x3', '0 odd: 3']


def test_nested_tries_rethrow_and_errors_in_a_catch():
    assert run_ok(HALF + main(
        'try\n'
        '    try\n'
        '        int x = half(5)\n'
        '        print("{x}")\n'
        '    finally\n'
        '        print("inner finally")\n'
        'catch e\n'
        '    print("outer caught: {e}")\n'
        'try\n'
        '    try\n'
        '        throw Error("first")\n'
        '    catch e\n'
        '        print("caught {e}")\n'
        '        throw e\n'
        '    finally\n'
        '        print("finally after catch")\n'
        'catch again\n'
        '    print("again {again}")\n'
        'try {\n'
        '    int y = half(7)\n'
        '    print("{y}")\n'
        '} catch {\n'
        '    print("bare catch")\n'
        '}'
    )) == ['inner finally', 'outer caught: odd: 5', 'caught first', 'finally after catch',
           'again first', 'bare catch']


def test_a_thrown_error_nobody_catches_stops_the_program():
    lines, stderr = run_failing(HALF + main(
        'try\n'
        '    print("{@1}", strict(1))\n'
        'finally\n'
        '    print("done")\n'
        'print("{@1}", strict(-1))'
    ))
    assert lines == ['1', 'done']
    assert 'Error at test.fusion:7: negative' in stderr


def test_capture_catches_a_thrown_error_too():
    assert run_ok(HALF + main(
        'int n, Error err = strict(-5)\n'
        'print("{n} {err}")'
    )) == ['0 negative']


def test_throw_an_error_held_in_a_variable_with_none():
    assert run_ok(main(
        'Error none = Error("x")\n'
        'Error e = Error("kept")\n'
        'try\n'
        '    throw e\n'
        'catch caught\n'
        '    print("{caught}")'
    )) == ['kept']


@pytest.mark.parametrize("body, message", [
    ('throw "oops"', "throw needs an Error"),
    ('try\n    print("x")\ncatch e\n    int n = e', "Cannot assign Error to variable of type int"),
])
def test_try_type_errors(body, message):
    assert message in errors_of(main(body))


@pytest.mark.parametrize("body, message", [
    ('try\n    print("x")\n', "A try needs a 'catch', a 'finally', or both"),
    ('try print("x")\ncatch\n    print("y")\n', "Expected the try block"),
])
def test_try_parse_errors(body, message):
    with pytest.raises(Exception, match=message):
        errors_of(main(body))
