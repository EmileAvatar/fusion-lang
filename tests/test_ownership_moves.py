"""Tests for Task 48.1 - moving (Ownership.md sections 1-2, truth tables 1 and 3; D.014,
D.097, D.102).

    [memory]
    assignment = "move"          // "share" (today's default, D.102) keeps two names, one object

A List, a Map, an object and a struct holding one of them move when handed over; using the
old name afterwards is a compile error until it gets a new value; `byVal` copies. Programs
that compile still run with the leak check - the counting is unchanged until 48.6.
"""

import pytest

from src.config.project_config import MemoryConfig, load_project_config
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import main, parse

MOVE = {'memory_config': MemoryConfig(assignment='move')}
CAR = 'class Car\n    public string color\n    constructor(string color)\n        this.color = color\n\n'


def errors(source: str, options=MOVE) -> list:
    analyzer = SemanticAnalyzer(**options)
    analyzer.analyze(parse(source))
    return [e.message for e in analyzer.get_errors()]


def run(source: str, options=MOVE) -> list:
    code, out, err = compile_and_run(source, analyzer_options=options)
    assert code == 0, err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


# ---------- truth table 1: each operation, by kind of value ----------

def test_assigning_an_object_moves_it():
    found = errors(CAR + main('Car a = Car("red")\nCar b = a\nprint(a.color)'))
    assert found == ["'a' was moved to 'b' on line 8 - use byVal a for a copy"]


def test_a_new_value_brings_it_back():
    assert run(CAR + main('Car a = Car("red")\nCar b = a\na = Car("blue")\n'
                          'print("{a.color} {b.color}")')) == ['blue red']


def test_by_val_copies():
    assert run(CAR + main('Car a = Car("red")\nCar b = byVal a\nb.color = "blue"\n'
                          'print("{a.color} {b.color}")')) == ['red blue']


@pytest.mark.parametrize('body', [
    'List<int> xs = [1]\nList<int> ys = xs\nprint("{@1}", xs.len())',
    'Map<string, int> m = Map<string, int>()\nMap<string, int> n = m\nprint("{@1}", m.len())',
])
def test_lists_and_maps_move(body):
    assert any('was moved to' in e for e in errors(main(body)))


@pytest.mark.parametrize('body', [
    'int a = 1\nint b = a\nprint("{a} {b}")',
    'string a = "x"\nstring b = a\nprint("{a} {b}")',
    'Point a = Point(1, 2)\nPoint b = a\nprint("{@1}", a.x)',
])
def test_numbers_strings_and_plain_structs_copy(body):
    assert errors('struct Point\n    int x\n    int y\n\n' + main(body)) == []


def test_a_struct_holding_a_list_moves_as_a_whole():
    source = 'struct Order\n    int id\n    List<int> items\n\n' + \
        main('Order a\na.id = 1\nOrder b = a\nprint("{@1}", a.id)')
    assert errors(source) == ["'a' was moved to 'b' on line 8 - use byVal a for a copy"]


def test_a_struct_holding_an_object_moves_as_a_whole():
    # D.097 (user, 2026-11-01): a struct made locally moves, its object with it
    source = CAR + 'struct Garage\n    Car car\n\n' + \
        main('Garage g = Garage()\ng.car = Car("red")\nGarage h = g\nprint(g.car.color)')
    assert any("'g' was moved to 'h'" in e for e in errors(source))


def test_adding_to_a_list_moves():
    found = errors(CAR + main('List<Car> cars = []\nCar c = Car("red")\ncars.add(c)\nprint(c.color)'))
    assert found == ["'c' was moved to 'cars' (add) on line 9 - use byVal c for a copy"]


def test_a_list_literal_moves():
    found = errors(CAR + main('Car c = Car("red")\nList<Car> cars = [c]\nprint(c.color)'))
    assert any("'c' was moved to a List" in e for e in found)


def test_a_field_set_moves():
    source = CAR + 'class Garage\n    public Car car\n\n' + \
        main('Garage g = Garage()\nCar c = Car("red")\ng.car = c\nprint(c.color)')
    assert any("'c' was moved to 'g.car'" in e for e in errors(source))


def test_an_interface_value_and_a_cast_move():
    source = 'interface Shape\n    int function sides()\n\n' \
             'class Square implements Shape\n    int function sides() : 4\n\n' + \
        main('Square q = Square()\nShape s = (Shape)q\nprint("{@1}", q.sides())')
    assert any("'q' was moved to 's'" in e for e in errors(source))


def test_returning_moves_to_the_caller():
    source = CAR + 'Car function make()\n    Car c = Car("red")\n    return c\n\n' + \
        main('Car mine = make()\nprint(mine.color)')
    assert run(source) == ['red']


def test_a_lambda_reading_a_moved_variable():
    source = CAR + main('Car a = Car("red")\nCar b = a\n(int) : string f = func(int x) : a.color\nprint(f(1))')
    assert any("'a' was moved to 'b'" in e for e in errors(source))


# ---------- truth table 3: paths through the code ----------

def test_moved_in_one_branch_is_maybe_moved_after():
    source = CAR + main('Car a = Car("red")\nCar b = Car("blue")\nif a.color == "red"\n'
                        '    b = a\nprint(a.color)')
    assert errors(source) == ["'a' may have been moved to 'b' on line 10 - give it a new value on "
                              "every path, or use byVal a for a copy"]


def test_every_branch_gives_a_new_value():
    source = CAR + main('Car a = Car("red")\nCar b = Car("blue")\nif a.color == "red"\n'
                        '    b = a\n    a = Car("green")\nprint(a.color)')
    assert run(source) == ['green']


def test_moved_in_a_loop_without_a_new_value():
    source = CAR + main('List<Car> cars = []\nCar c = Car("red")\nfor i in range(0, 3)\n    cars.add(c)')
    assert errors(source) == ["'c' was moved to 'cars' (add) on line 10, in an earlier pass of the "
                              "loop - give it a new value each pass, or use byVal c for a copy"]


def test_a_loop_giving_a_new_value_each_pass():
    source = CAR + main('List<Car> cars = []\nCar c = Car("red")\nfor i in range(0, 3)\n'
                        '    cars.add(c)\n    c = Car("blue")\nprint("{@1} {c.color}", cars.len())')
    assert run(source) == ['3 blue']


def test_a_variable_made_inside_the_loop():
    source = CAR + main('List<Car> cars = []\nfor i in range(0, 2)\n    Car c = Car("red")\n'
                        '    cars.add(c)\nprint("{@1}", cars.len())')
    assert run(source) == ['2']


def test_moved_in_a_loop_used_after_it():
    source = CAR + main('List<Car> cars = []\nCar c = Car("red")\nwhile cars.len() < 1\n'
                        '    cars.add(c)\nprint(c.color)')
    found = errors(source)
    assert len(found) == 2 and "'c' may have been moved" in found[1], found


def test_moved_in_a_try_is_maybe_moved_in_the_catch():
    source = CAR + main('Car a = Car("red")\nCar b = Car("blue")\ntry\n    b = a\n'
                        '    throw Error("x")\ncatch Error e\n    print(a.color)')
    assert any("'a' may have been moved" in e for e in errors(source))


def test_a_break_path_is_followed():
    source = CAR + main('Car a = Car("red")\nCar b = Car("blue")\nwhile true\n'
                        '    b = a\n    break\nprint(a.color)')
    assert any("'a' may have been moved" in e or "'a' was moved" in e for e in errors(source))


# ---------- nulls (Rule 4b) ----------

def test_without_a_null_check_a_moved_null_is_a_null_error():
    source = CAR + main('Car a\nCar b = a\ntry\n    print(b.color)\ncatch NullError e\n    print("null")')
    assert run(source) == ['null']


def test_with_a_null_check_the_code_runs_on():
    source = CAR + main('Car a\nCar b = a\nif b is not null\n    print(b.color)\nprint("done")')
    assert run(source) == ['done']


# ---------- the setting ----------

def test_share_keeps_two_names_on_one_object():
    source = CAR + main('Car a = Car("red")\nCar b = a\nb.color = "blue"\nprint(a.color)')
    assert errors(source, {}) == []
    assert run(source, {}) == ['blue']
    assert MemoryConfig().assignment == 'share'          # the default while Task 48 is built


def test_the_setting_is_read(tmp_path):
    (tmp_path / 'fusion.toml').write_text('[memory]\nassignment = "move"\n')
    (tmp_path / 'p.fusion').write_text('')
    assert load_project_config(str(tmp_path / 'p.fusion')).memory.assignment == 'move'


def test_a_bad_value_is_an_error(tmp_path):
    from src.config.project_config import ProjectConfigError
    (tmp_path / 'fusion.toml').write_text('[memory]\nassignment = "copy"\n')
    (tmp_path / 'p.fusion').write_text('')
    with pytest.raises(ProjectConfigError, match='memory.assignment must be'):
        load_project_config(str(tmp_path / 'p.fusion'))


def test_a_case_name_is_a_new_variable():
    # selfhost codegen: `case Function(name, params)` after an outer `params` was moved
    source = 'enum Shape\n    Box(List<int> sizes)\n    Dot\n\nstruct Keep\n    List<int> sizes\n\n' + \
        main('List<int> sizes = [1]\nKeep k = Keep(sizes)\nShape s = Shape.Box([2, 3])\nmatch s\n'
             '    case Box(sizes)\n        print("{@1}", sizes.len())\n    case Dot\n        print("dot")')
    assert errors(source) == []
