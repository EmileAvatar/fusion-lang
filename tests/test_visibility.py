"""Tests for Task 32.2a - what is public when nothing is written (Classes.md section 1).

Inside a class: fields private, functions and constructors public - `public` / `private`
written out changes one member. At module level: structs, classes and enums public; functions
and module variables private (Task 18.4.3, unchanged). Each test is a row of the table.
"""

import pytest

from tests.test_end_to_end import compile_and_run
from tests.test_modules import errors as module_errors
from tests.test_structs import errors_of, main

CAR = ('class Car\n'
       '    string name                      // private (the default)\n'
       '    public int speed = 10\n'
       '    private constructor(string name)\n'
       '        this.name = name\n'
       '    string function getName() : name // public (the default) - its own field\n'
       '    private void function tune()\n'
       '        speed = speed + 1\n'
       '    void function checkUp()\n'
       '        tune()                       // a private function inside the class\n'
       '    Car function twin() : Car(name)  // a private constructor inside the class\n'
       '    Car function rename(Car other)\n'
       '        other.name = name            // another Car\'s private field - the same class\n'
       '        return other\n\n'
       'class Garage\n'
       '    Car function fix(Car c)\n'
       '        c.checkUp()\n'
       '        return c\n\n')


def test_inside_the_class_everything_is_open():
    code, out, err = compile_and_run(
        CAR.replace('    private constructor', '    constructor')
        + main('Car c = Car("Honda")\n'
               'c.checkUp()\n'
               'Car t = c.twin()\n'
               'print("{@1} {@2} {@3}", c.getName(), c.speed, t.rename(Car("x")).getName())'))
    assert code == 0, err
    assert out.strip().splitlines() == ['Honda 11 Honda']


@pytest.mark.parametrize('body, message', [
    ('Car c = Car("x")\nprint(c.name)',
     "The constructor of class 'Car' is private - only Car itself makes Car objects"),
    ('Car c\nstring n = c.name',
     "Field 'name' of class 'Car' is private - only Car's own functions can use it "
     "(write 'public' before it to share it)"),
    ('Car c\nc.name = "x"', "Field 'name' of class 'Car' is private"),
    ('Car c\nc.tune()', "Function 'tune' of class 'Car' is private - only Car's own functions "
                        "can call it"),
])
def test_outside_the_class_private_is_an_error(body, message):
    assert message in errors_of(CAR + main(body))


def test_outside_the_class_public_members_work():
    # speed is written public; getName and checkUp are public by default
    assert errors_of(CAR + 'void function use(Car c)\n'
                           '    c.speed = 5\n'
                           '    c.service()\n'
                           '    print(c.getName())\n\n'
                     + main('int n = 1\nn = n / 0')).count('private') == 0


def test_module_level_types_are_public_functions_private(tmp_path):
    files = {
        'shop/items.fusion': ('struct Item\n    int n\n\n'
                              'class Cart\n    public int count\n\n'
                              'enum Kind: Small Big\n\n'
                              'private struct Note\n    int n\n\n'
                              'int function helper() : 1\n'),
        'main.fusion': ('import shop\n\n'
                        'void function main()\n'
                        '    shop.Item i\n'
                        '    shop.Cart c\n'
                        '    shop.Kind k\n'
                        '    print("{@1}", i.n)\n'),
    }
    assert module_errors(str(tmp_path), files) == ''
    files['main.fusion'] = 'import shop\n\nvoid function main()\n    shop.Note n\n'
    assert "'Note' is private to module 'shop'" in module_errors(str(tmp_path), files)
    files['main.fusion'] = 'import shop\n\nvoid function main()\n    int x = shop.helper()\n'
    assert "'helper' is private to module 'shop'" in module_errors(str(tmp_path), files)
