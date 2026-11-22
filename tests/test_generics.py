"""Task 33.2a - generic functions of the program's own (D.166, D.168).

    T function first<T>(List<T> items) : items[0]
    T function last(List<T> items) : ...              // T, K, V (and T1, K2) in a signature
    V function valueOf<K, V>(Map<K, V> m, K key) : m[key]
    T1 function second<T, T1>(List<T> a, List<T1> b) : b[0]

    first(numbers)          // the types from the arguments (preferred)
    first<int>(numbers)     // or written

One C function per set of types used. Every program runs under the leak check; one type and several
(<T>, <T, T1>, <K, V>) with numbers, strings, structs and objects.
"""

import pytest

from src.config.project_config import GenericsConfig, ProjectConfigError, _load_generics_section
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import parse

GENERICS = ('T function first<T>(List<T> items) : items[0]\n\n'
            'T function last(List<T> items) : items[items.len() - 1]\n\n'
            'V function valueOf<K, V>(Map<K, V> m, K key) : m[key]\n\n'
            'T1 function second<T, T1>(List<T> a, List<T1> b) : b[0]\n\n'
            'T function pick<T>(bool firstOne, T a, T b)\n'
            '    if firstOne\n'
            '        return a\n'
            '    return b\n\n'
            'int function count<T>(T[] items) : items.length\n\n'
            'class Car\n'
            '    public string name\n'
            '    constructor(string name)\n'
            '        this.name = name\n\n'
            'struct Point\n'
            '    int x\n'
            '    int y\n\n')


def run(main_body: str, top: str = GENERICS, **options) -> list:
    source = top + 'void function main()\n' + ''.join(f'    {line}\n' for line in main_body.split('\n'))
    code, out, err = compile_and_run(source, analyzer_options=options or None)
    assert code == 0, out + err
    return [line for line in out.strip().splitlines() if not line.startswith('[freed')]


def errors_of(main_body: str, top: str = GENERICS, **options) -> list:
    source = top + 'void function main()\n' + ''.join(f'    {line}\n' for line in main_body.split('\n'))
    analyzer = SemanticAnalyzer(**options)
    analyzer.analyze(parse(source))
    return [e.message for e in analyzer.get_errors()]


def test_one_type_from_the_arguments():
    assert run('List<int> numbers = [3, 1, 2]\nList<string> names = ["Ada", "Bo"]\n'
               'print("{@1} {@2} {@3}", first(numbers), first(names), last(names))') == ['3 Ada Bo']


def test_the_types_written():
    assert run('List<int> numbers = [3, 1, 2]\nprint("{@1}", first<int>(numbers))') == ['3']


def test_several_types():
    # <K, V> and <T, T1> - kept as a test going forward (user, 2026-11-22)
    body = ('Map<string, int> ages\nages["Ada"] = 36\n'
            'List<int> numbers = [3, 1, 2]\nList<string> names = ["Ada", "Bo"]\n'
            'print("{@1} {@2} {@3}", valueOf(ages, "Ada"), second(numbers, names), second(names, numbers))\n'
            'print("{@1}", valueOf<string, int>(ages, "Ada"))')
    assert run(body) == ['36 Ada 3', '36']


@pytest.mark.parametrize('body, line', [
    ('print("{@1}", pick(true, 1, 2))', '1'),                                  # numbers
    ('print("{@1}", pick(false, "a", "b"))', 'b'),                             # strings - copied, freed
    ('Point p = pick(false, Point(1, 2), Point(3, 4))\nprint("{@1}", p.x)', '3'),     # structs
    ('Car c = pick(true, Car("Ada"), Car("Bo"))\nprint(c.name)', 'Ada'),     # objects - counted
    ('List<Car> cars = [Car("Ada"), Car("Bo")]\nprint(first(cars).name)', 'Ada'),
    ('int[] xs = [5, 6, 7]\nprint("{@1}", count(xs))', '3'),                    # T[]
])
def test_numbers_strings_structs_objects(body, line):
    assert run(body) == [line]


def test_one_copy_per_set_of_types():
    program = parse(GENERICS + 'void function main()\n    List<int> a = [1]\n    List<int> b = [2]\n'
                               '    print("{@1} {@2}", first(a), first(b))\n'
                               '    List<string> c = ["x"]\n    print(first(c))\n')
    SemanticAnalyzer().analyze(program)
    names = [d.name for d in program.declarations if getattr(d, 'generic_of', None) == 'first']
    assert names == ['first__int', 'first__string']


def test_a_generic_calls_a_generic_and_itself():
    top = ('T function first<T>(List<T> items) : items[0]\n\n'
           'T function head<T>(List<T> items) : first(items)\n\n'
           'T function lastOf<T>(List<T> items, int i)\n'
           '    if i == items.len() - 1\n'
           '        return items[i]\n'
           '    return lastOf(items, i + 1)\n\n')
    assert run('List<string> names = ["a", "b", "c"]\nprint("{@1} {@2}", head(names), lastOf(names, 0))',
               top=top) == ['a c']


@pytest.mark.parametrize('body, message', [
    ('List<int> xs = [1]\nint a = first<int, string>(xs)', "'first' has 1 type parameter(s) (T) - 2 written"),
    ('List<int> xs = [1]\nstring a = first(xs)', 'Cannot assign int'),
    ('int a = pick(true, 1, "two")', 'pick'),
])
def test_wrong_uses_are_errors(body, message):
    assert any(message in e for e in errors_of(body)), errors_of(body)


def test_a_type_that_cant_be_worked_out_says_write_it():
    top = 'T function make<T>() : make<T>()\n\n'
    found = errors_of('int a = make()', top=top)
    assert any("T can't be worked out from the arguments - write the types: make<int>(...)" in e
               for e in found), found


@pytest.mark.parametrize('name', ['T', 'K', 'V', 'T1'])
def test_a_struct_named_t_k_v_is_an_error(name):
    found = errors_of('print("x")', top=f'struct {name}\n    int x\n\n')
    assert any('T, K and V (and T1, K2 ...) name a generic' in e for e in found), found


def test_generics_off_in_the_project():
    found = errors_of('print("x")', generics_config=GenericsConfig(enabled=False))
    assert any("generics are off in this project ([generics] enabled = false" in e for e in found), found
    assert errors_of('List<int> xs = [1]\nprint("{@1}", xs.len())', top='',
                     generics_config=GenericsConfig(enabled=False)) == []      # List<T> stays


def test_the_setting():
    assert _load_generics_section({'generics': {'enabled': False}}, 'fusion.toml').enabled is False
    with pytest.raises(ProjectConfigError, match='must be true or false'):
        _load_generics_section({'generics': {'enabled': 'no'}}, 'fusion.toml')


def test_a_comparison_is_still_a_comparison():
    # a < b > (c) - not types: only type words between < and > make a written call
    assert run('int a = 1\nint b = 2\nbool r = a < b\nprint("{@1}", r)', top='') == ['true']
