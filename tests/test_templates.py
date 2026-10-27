"""Tests for Task 29.3 - string templates.

    template string greet = "Hello {@1}, you are {@2} - welcome to {shop}"

A template is a fixed text that works as a function (user design, 2026-10-27): greet("Ann",
30) fills each {@N} from the arguments - any printable value - and reads {shop} when it is
called. A template declared in a function is expanded where it is called, so {name} can be
one of that function's variables; passing it on would need a closure. A module-level
template uses module variables and constants only, and can be passed where a function type
is written (4b). `template` is only special before `string` and a name.
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_modules import errors as module_errors, run_project
from tests.test_structs import main


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def analyze(source: str) -> SemanticAnalyzer:
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return analyzer


def errors(source: str) -> list:
    return [str(e) for e in analyze(source).get_errors()]


def test_a_local_template_reads_the_variables_when_called():
    lines = run(main('string city = "Paris"\n'
                     'template string greet = "Hello {@1}, you are {@2} - {city}"\n'
                     'print(greet("Ann", 30))\n'
                     'city = "Rome"\n'
                     'string text = greet("Bob", true)\n'
                     'print(text)'))
    assert lines == ['Hello Ann, you are 30 - Paris', 'Hello Bob, you are true - Rome']


def test_placeholders_in_any_order_and_repeated_and_no_values():
    lines = run(main('template string twice = "{@2}-{@1}-{@2}"\n'
                     'template string plain = "no values"\n'
                     'print(twice(\'a\', 7))\n'
                     'print(plain())'))
    assert lines == ['7-a-7', 'no values']


MODULE_TEMPLATE = ('const string SHOP = "Ann\'s"\n'
                   'template string welcome = "Welcome to {SHOP}, {@1}!"\n\n'
                   'void function show((string) -> string line, string who)\n'
                   '    print(line(who))\n\n')


def test_a_module_template_is_called_and_passed_as_a_function_value():
    lines = run(MODULE_TEMPLATE + main('print(welcome("Cy"))\n'
                                       'show(welcome, "Di")\n'
                                       'show(line = welcome, who = "Ed")\n'
                                       '(string) -> string f = welcome\n'
                                       'print(f("Fi"))'))
    assert lines == ["Welcome to Ann's, " + n + '!' for n in ('Cy', 'Di', 'Ed', 'Fi')]


def test_template_is_still_an_ordinary_name():
    lines = run(main('string template = "a name"\n'
                     'print(template)'))
    assert lines == ['a name']


@pytest.mark.parametrize('source, message', [
    (main('template string g = "{@1} {@3}"\nprint(g(1, 2, 3))'),
     "Template 'g' has {@3} but no {@2} - number the values from 1 without gaps"),
    (main('template string g = "{@1} {@2}"\nprint(g(1))'),
     "Template 'g' takes 2 value(s) ({@1}, {@2}), got 1"),
    (main('template string g = "hi"\nprint(g(1))'),
     "Template 'g' takes 0 value(s), got 1"),
    ('string function nobody() : "x"\n\ntemplate string g = "Hi {who} {@1}"\n\n'
     + main('print(g(1))'),
     "Template 'g' uses '{who}' - a template outside any function can only use module "
     "variables and constants"),
    (main('template string g = "Hi {missing}"\nprint(g())'), "Undefined variable: 'missing'"),
    (main('template string g = "{@1}"\nstring s = g'), "Template 'g' is used by calling it"),
    (main('template string g = "{@1}"\nstring g = "x"'),
     "'g' is already a template - choose another name for the variable"),
    (main('template string g = "{@1}"\ntemplate string g = "{@2}"\nprint(g(1))'),
     "'g' is already used - choose another name for the template"),
    (main('template string g = "{@1}"\nprint(g(who = 1))'),
     "Template 'g' takes its values in order"),
])
def test_template_errors(source, message):
    found = errors(source)
    assert any(message in e for e in found), found


def test_a_local_template_using_local_variables_cannot_be_passed_on():
    found = errors('void function show((string) -> string line)\n'
                   '    print(line("x"))\n\n'
                   + main('string shop = "A"\n'
                          'template string g = "{@1} at {shop}"\n'
                          'show(g)'))
    assert found and "uses '{shop}' from this function" in found[0]
    assert len(found) == 1          # nothing repeated after it


def test_a_function_type_that_does_not_fit():
    found = errors(MODULE_TEMPLATE + main('(string, string) -> string f = welcome'))
    assert any("takes 1 value(s) and gives a string - it doesn't fit" in e for e in found)


def test_an_error_in_the_text_is_reported_once_at_the_template():
    found = errors(main('template string g = "Hi {missing} {@1}"\n'
                        'print(g(1))\n'
                        'print(g(2))'))
    assert found == [e for e in found if 'missing' in e] and len(found) == 1
    assert ':2:' in found[0]                # the template's line, not 1:1


def test_an_unused_template_is_a_warning():
    warnings = [str(w) for w in analyze(main('template string g = "x"')).get_warnings()]
    assert any("Template 'g' is never used" in w for w in warnings)


def test_each_module_has_its_own_templates(tmp_path):
    files = {'main.fusion': 'import shop\n\ntemplate string banner = "main {@1}"\n\n'
                            + main('print(banner("x"))\nprint(shop.sign("open"))'),
             'shop/shop.fusion': 'public const string NAME = "Ann\'s"\n'
                                 'template string banner = "*** {NAME}: {@1} ***"\n\n'
                                 'public string function sign(string text) : banner(text)\n'}
    assert run_project(str(tmp_path), files) == ['main x', "*** Ann's: open ***"]


def test_a_template_is_private_to_its_module(tmp_path):
    files = {'main.fusion': 'import shop\n\n' + main('print(shop.banner("x"))'),
             'shop/shop.fusion': 'template string banner = "{@1}"\n\n'
                                 'public string function sign(string t) : banner(t)\n'}
    assert "'banner' is private to module 'shop'" in module_errors(str(tmp_path), files)
