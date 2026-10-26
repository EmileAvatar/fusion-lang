"""Tests for Task 44.2 - any function can be called as a method on its first argument.

`p.moved(1, 2)` is `moved(p, 1, 2)` when the program has a function `moved` whose first
parameter takes p. What comes first, so nothing that worked before changes meaning: a
List / Map method (`xs.add`), and an enum's own toString / toInt. (A struct field can't hold
a function - structs hold plain values only - so a field never competes.)
Like a plain call, the program's own function replaces a library function of the same name.
The method gets a copy, as any function does (structs are values): `p = p.moved(1, 2)`.
"""

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run

POINT = ('struct Point\n'
         '    int x\n'
         '    int y\n\n'
         'Point function moved(Point p, int dx, int dy) : Point(p.x + dx, p.y + dy)\n\n')


def run(source: str) -> list:
    code, out, err = compile_and_run(source)
    assert code == 0, err
    return out.strip().splitlines()


def errors(source: str) -> list:
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return [str(e) for e in analyzer.get_errors()]


def test_a_struct_function_as_a_method_and_chained():
    lines = run(POINT + 'void function main()\n'
                        '    Point p = Point(1, 2)\n'
                        '    Point q = p.moved(10, 20).moved(1, 1)\n'
                        '    print("{p.x} {p.y} {q.x} {q.y}")\n')
    assert lines[0] == '1 2 12 23'          # p itself is unchanged: the method got a copy


def test_built_in_types_lists_maps_and_enums():
    lines = run('enum Light: Red Green\n\n'
                'int function twice(int n) : n * 2\n'
                'string function shout(string s) : s.toUpper() + "!"\n'
                'int function total(List<int> xs) : xs.reduce(0, (int a, int b) : a + b)\n'
                'int function size(Map<string, int> m) : m.len()\n'
                'bool function isRed(Light l) : l == Light.Red\n\n'
                'void function main()\n'
                '    List<int> xs = [1, 2, 3]\n'
                '    Map<string, int> m\n'
                '    m["a"] = 1\n'
                '    print("{@1} {@2} {@3} {@4} {@5}", 21.twice(), "hi".shout(), xs.total(), m.size(), Light.Red.isRed())\n')
    assert lines[0] == '42 HI! 6 1 true'


def test_list_map_and_enum_methods_come_first():
    lines = run('enum Light: Red Green\n\n'
                'int function reduce(List<int> xs) : 99\n'
                'string function toString(Light l) : "mine"\n\n'
                'void function main()\n'
                '    List<int> xs = [1, 2]\n'
                '    print("{@1} {@2}", xs.reduce(0, (int a, int b) : a + b), Light.Green.toString())\n')
    assert lines[0] == '3 Green'


def test_the_programs_function_replaces_a_library_one_as_a_method_too():
    lines = run('string function trim(string s) : "[" + s + "]"\n\n'
                'void function main()\n'
                '    print("x".trim())\n')
    assert lines[0] == '[x]'


def test_a_function_that_does_not_take_the_value_is_not_a_method():
    found = errors(POINT + 'void function main()\n'
                           '    int n = 5\n'
                           '    Point p = n.moved(1, 2)\n')
    assert any("Int has no method 'moved'" in e for e in found), found


def test_wrong_arguments_are_reported_like_any_call():
    found = errors(POINT + 'void function main()\n'
                           '    Point p = Point(1, 2)\n'
                           '    Point q = p.moved("a", 2)\n')
    assert found, found
