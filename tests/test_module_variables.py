"""Tests for Task 44.1 - module-level variables and constants.

`int count = 0`, `const int LIMIT = 3`, `public string version = "1.0"` outside any function:
- set in the order written, before main's own code; an initializer may use the functions and
  the module variables above it
- every function of the module sees them; other modules see the public ones (`m.version`)
- strings, lists and structs in them are freed when main ends (the leak check runs on every
  end-to-end test here)
- a name inside a function can't hide one; `[modules] variables = false` turns variables off
  (constants stay allowed)
"""

import pytest

from src.config import ModulesConfig
from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_modules import errors as project_errors, run_project


def check(source: str, **config) -> list:
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer(**config)
    analyzer.analyze(program)
    return [str(e) for e in analyzer.get_errors()]


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def test_variables_shared_by_functions():
    lines = run('int count = 0\n'
                'string log = "start"\n'
                'List<string> names = ["a"]\n\n'
                'void function record(string what)\n'
                '    count = count + 1\n'
                '    log = log + ", " + what\n'
                '    names.add(what)\n\n'
                'void function main()\n'
                '    record("x")\n'
                '    record("y")\n'
                '    print("{count} | {log} | {@1}", names.len())\n')
    assert lines[0] == '2 | start, x, y | 3'


def test_constants_arrays_and_order_of_setting():
    lines = run('const int LIMIT = 3\n'
                'int[] primes = [2, 3, 5]\n'
                'int doubled = LIMIT * 2\n'
                'string greeting = "hi " + toString(doubled)\n\n'
                'void function main()\n'
                '    print("{@1} {@2} {doubled} {greeting}", primes[LIMIT - 1], len(primes))\n')
    assert lines[0] == '5 3 6 hi 6'


def test_a_variable_without_a_value_starts_empty_and_a_struct_one_too():
    lines = run('struct Player\n'
                '    string name\n'
                '    int score = 10\n\n'
                'string note\n'
                'Player best\n\n'
                'void function main()\n'
                '    best.name = "Ada"\n'
                '    note = note + "set"\n'
                '    print("[{note}] {best.name} {best.score}")\n')
    assert lines[0] == '[set] Ada 10'


def test_an_initializer_may_call_a_function():
    lines = run('int function start() : 40 + 2\n\n'
                'int answer = start()\n\n'
                'void function main()\n'
                '    print("{answer}")\n')
    assert lines[0] == '42'


def test_a_lambda_may_use_a_module_variable():
    lines = run('int base = 100\n\n'
                'void function main()\n'
                '    (int) : int add = func(int x) : x + base\n'
                '    print("{@1}", add(5))\n')
    assert lines[0] == '105'


@pytest.mark.parametrize('source, message', [
    ('int count = 0\n\nvoid function main()\n    int count = 1\n',
     "Variable 'count' has the same name as the module variable 'count'"),
    ('int x = 0\n\nint function f(int x) : x\n\nvoid function main()\n    print("{@1}", f(1))\n',
     "Parameter 'x' has the same name as the module variable 'x'"),
    ('int i = 0\n\nvoid function main()\n    for i in range(0, 2)\n        print("{i}")\n',
     "Loop variable 'i' has the same name as the module variable 'i'"),
    ('const int LIMIT = 3\n\nvoid function main()\n    LIMIT = 4\n', 'LIMIT'),
    ('int a = b\nint b = 1\n\nvoid function main()\n    print("{a}")\n', "'b'"),
    ('int x = 1\nint x = 2\n\nvoid function main()\n    print("{x}")\n', "'x'"),
    ('string s = 5\n\nvoid function main()\n    print(s)\n', 'string'),
])
def test_mistakes_are_errors(source, message):
    found = check(source)
    assert any(message in e for e in found), found


def test_the_setting_turns_variables_off_but_not_constants():
    source = ('const int LIMIT = 3\nint count = 0\n\n'
              'void function main()\n    print("{@1} {count}", LIMIT)\n')
    found = check(source, modules_config=ModulesConfig(variables=False))
    assert len(found) == 1 and "[modules] variables = false" in found[0], found
    assert check('const int LIMIT = 3\n\nvoid function main()\n    print("{@1}", LIMIT)\n',
                 modules_config=ModulesConfig(variables=False)) == []


def test_capturing_an_error_outside_a_function_is_a_syntax_error():
    with pytest.raises(ParserError, match='only works inside a function'):
        Parser(Lexer('int n, err = toInt("1")\n', 't.fusion').tokenize()).parse_program()


def test_a_module_shares_its_public_variables(tmp_path):
    files = {
        'stats/counter.fusion': ('public int total = 0\n'
                                 'public const string NAME = "stats"\n'
                                 'int hidden = 7\n\n'
                                 'public void function add(int n)\n'
                                 '    total = total + n + hidden - hidden\n'),
        'main.fusion': ('import stats\n\n'
                        'void function main()\n'
                        '    stats.add(5)\n'
                        '    stats.add(2)\n'
                        '    print("{@1} {@2}", stats.NAME, stats.total)\n'),
    }
    assert run_project(str(tmp_path), files) == ['stats 7']


def test_a_private_module_variable_is_private(tmp_path):
    files = {
        'stats/counter.fusion': 'int hidden = 7\n\npublic int function f() : hidden\n',
        'main.fusion': 'import stats\n\nvoid function main()\n    print("{@1}", stats.hidden)\n',
    }
    assert "'hidden' is private to module 'stats'" in project_errors(str(tmp_path), files)


def test_the_interface_lists_public_module_variables(tmp_path):
    from src.modules import program_interfaces
    from tests.test_modules import write_project
    main_file = write_project(str(tmp_path), {
        'stats/counter.fusion': ('public int total = 0\npublic const string NAME = "stats"\n'
                                 'int hidden = 7\n'),
        'main.fusion': 'import stats\n\nvoid function main()\n    print("{@1}", stats.total)\n',
    })
    lines, problems = program_interfaces(main_file, None, None)
    assert problems == []
    assert '    public const string NAME' in lines and '    public int total' in lines
    assert not any('hidden' in line for line in lines)
