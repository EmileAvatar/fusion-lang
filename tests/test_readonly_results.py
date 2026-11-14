"""Task 50 - readonly results (D.110, D.113) and a deep const on objects (D.112).

One test per row of the truth table in files/Ownership.md section 4 ("readonly results and const
objects"), and null both ways (Rule 4b).
"""
import pytest

from src.parser.parser import ParserError
from src.semantic import SemanticAnalyzer
from tests.test_ownership_moves import run
from tests.test_structs import main, parse

CL = ('class Engine\n'
      '    public int power = 90\n'
      '    void function tune()\n'
      '        this.power = 100\n\n'
      'class Car\n'
      '    public string name = "Mini"\n'
      '    public Engine engine = Engine()\n'
      '    public readonly Engine function getEngine()\n'
      '        return this.engine\n'
      '    void function rename(string n)\n'
      '        this.name = n\n\n'
      'void function boost(Engine e)\n'
      '    e.power = 120\n\n'
      'void function show(Engine e)\n'
      '    print("{@1}", e.power)\n\n')


def check(body: str, extra: str = ''):
    analyzer = SemanticAnalyzer()
    analyzer.analyze(parse(CL + extra + main(body)))
    return [e.message for e in analyzer.get_errors()], [w.message for w in analyzer.warnings]


# ---------- a readonly result ----------

ALLOWED = {
    'read a field': 'Car c = Car()\nEngine e = c.getEngine()\nprint("{@1}", e.power)',
    'pass to a function that only reads it': 'Car c = Car()\nEngine e = c.getEngine()\nshow(e)',
    'byVal - a copy that may change': 'Car c = Car()\nEngine e = byVal c.getEngine()\ne.power = 1\nshow(e)',
    'const object: read it': 'const Car c = Car()\nprint(c.name)',
    'const object: byVal copy may change': 'const Car c = Car()\nCar d = byVal c\nd.rename("x")\nprint(d.name)',
    'const object: its own set-up block': 'const Car c = Car() { c.name = "Golf" }\nprint(c.name)',
}

REFUSED = {
    'set a field': ('Car c = Car()\nEngine e = c.getEngine()\ne.power = 1',
                    "'e' holds the readonly result of getEngine - it may be read but not changed"),
    'a method that changes it': ('Car c = Car()\nEngine e = c.getEngine()\ne.tune()',
                                 "'e' holds the readonly result of getEngine - tune changes it"),
    'pass to a function that changes it': ('Car c = Car()\nEngine e = c.getEngine()\nboost(e)',
                                           "'e' holds the readonly result of getEngine - boost changes it"),
    'keep it in a List': ('Car c = Car()\nList<Engine> spares = []\nEngine e = c.getEngine()\nspares.add(e)',
                          "'e' holds the readonly result of getEngine - it can't be kept"),
    'byRef on it': ('Car c = Car()\nEngine e = byRef c.getEngine()',
                    "byRef asks to change getEngine's readonly result"),
    'change it directly': ('Car c = Car()\nc.getEngine().power = 3',
                           "getEngine gives a readonly result - it may be read but not changed"),
    'pass it directly to a change': ('Car c = Car()\nboost(c.getEngine())',
                                     "getEngine gives a readonly result - boost changes it"),
    'const object: set a field': ('const Car c = Car()\nc.name = "x"',
                                  "'c' is const - it may be read but not changed"),
    'const object: a method that changes it': ('const Car c = Car()\nc.rename("x")',
                                               "'c' is const - rename changes it"),
    'const object: pass to a function that changes it': ('const Engine k = Engine()\nboost(k)',
                                                         "'k' is const - boost changes it"),
}


@pytest.mark.parametrize('case', ALLOWED)
def test_allowed(case):
    errors, _ = check(ALLOWED[case])
    assert errors == []


@pytest.mark.parametrize('case', REFUSED)
def test_refused(case):
    body, message = REFUSED[case]
    errors, _ = check(body)
    assert any(message in e for e in errors), errors


def test_return_readonly_in_the_body_is_an_error():
    with pytest.raises(ParserError, match='readonly goes in the signature'):
        parse('class Box\n    public int n\n    int function value()\n        return readonly this.n\n\n'
              + main('print("x")'))


def test_readonly_on_a_number_result_is_a_warning():
    extra = 'class Bike\n    public readonly int function wheels()\n        return 2\n\n'
    errors, warnings = check('Bike b = Bike()\nprint("{@1}", b.wheels())', extra)
    assert errors == []
    assert warnings == ["readonly does nothing on wheels's result - a int is copied anyway (D.113)"]


def test_readonly_before_a_variable_is_an_error():
    with pytest.raises(ParserError, match="marks a function's result"):
        parse('class Box\n    readonly int n\n\n' + main('print("x")'))


def test_a_readonly_result_runs():
    assert run(CL + main('Car c = Car()\nEngine e = c.getEngine()\nshow(e)\n'
                         'Engine f = byVal c.getEngine()\nf.power = 7\nshow(f)\nshow(c.getEngine())')) == \
        ['90', '7', '90']


# ---------- null both ways (Rule 4b) ----------

NULL_CAR = ('class Engine\n    public int power = 90\n\n'
            'class Car\n    public Engine engine\n'
            '    public readonly Engine function getEngine()\n        return this.engine\n\n')


def test_a_null_readonly_result_without_a_check_is_a_null_error():
    assert run(NULL_CAR + main('Car c = Car()\nEngine e = c.getEngine()\n'
                               'try\n    print("{@1}", e.power)\ncatch err\n    print("caught")')) == ['caught']


def test_a_null_readonly_result_with_a_check_runs_on():
    assert run(NULL_CAR + main('Car c = Car()\nEngine e = c.getEngine()\n'
                               'if e is null\n    print("no engine")\nelse\n    print("{@1}", e.power)')) == \
        ['no engine']
