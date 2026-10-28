"""Tests for Task 30.12 - `case null`, and `break` ending a match.

A match can have one `case null`, on any value (user, 2026-10-28: a library or module may
hand over a null; strings may be nullable by a setting). A null equals no case value: it
goes to `case null`, else to `else`. With `case null`, a match that covers every value no
longer raises a NullError. `break` inside a match ends the match (as in a switch); `continue`
still acts on the loop around it.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, errors_of

STATUS = 'enum Status\n    OK\n    NotFound\n\n'


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def test_case_null_on_an_enum_and_with_other_values():
    lines = run(STATUS
                + 'string function name(Status s)\n'
                  '    match s\n'
                  '        case null: return "unset"\n'
                  '        case OK: return "ok"\n'
                  '        case NotFound: return "missing"\n\n'
                + main('Status s\n'
                       'print(name(s))\n'
                       'print(name(Status.NotFound))\n'
                       'match s\n'
                       '    case OK, null: print("ok or null")\n'
                       '    else: print("else")'))
    assert lines == ['unset', 'missing', 'ok or null']


def test_case_null_on_a_string_is_allowed_and_never_taken():
    lines = run(main('string day = "Monday"\n'
                     'match day\n'
                     '    case null: print("no day")\n'
                     '    case "Monday": print("start")\n'
                     '    else: print("other")'))
    assert lines == ['start']


def test_break_ends_the_match_and_frees_what_the_case_owns():
    lines = run(main('string day = "Monday"\n'
                     'match day\n'
                     '    case "Monday"\n'
                     '        string shout = day + "!"\n'
                     '        print(shout)\n'
                     '        if shout.length > 3\n'
                     '            break\n'
                     '        print("not reached")\n'
                     '    else: print("other")\n'
                     'print("after")'))
    assert lines == ['Monday!', 'after']        # the leak check covers `shout`


def test_break_inside_a_try_inside_a_match_runs_the_finally():
    lines = run(main('int n = 1\n'
                     'match n\n'
                     '    case 1\n'
                     '        try\n'
                     '            break\n'
                     '        finally\n'
                     '            print("finally")\n'
                     '    else: print("other")\n'
                     'print("after")'))
    assert lines == ['finally', 'after']


def test_break_in_a_match_outside_any_loop_is_fine():
    assert run(main('match 2\n    case 2: break\n    else: print("x")\nprint("ok")')) == ['ok']


@pytest.mark.parametrize('source, message', [
    (STATUS + main('Status s\nmatch s\n    case null: print("a")\n    case null: print("b")\n'
                   '    else: print("c")'), "A match can have only one 'case null'"),
    (main('Error e = Error("x")\nmatch e\n    case null: print("a")\n    else: print("b")'),
     "An Error is never null"),
    (main('break'), "Break statement outside loop"),
])
def test_errors(source, message):
    assert message in errors_of(source)
