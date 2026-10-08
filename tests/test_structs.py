"""Tests for Task 18.2 - structs.

18.2.1: core structs - declaration (three block styles), generated positional constructor,
        field defaults, `.` field access and assignment, value semantics (copy on assign,
        pass and return), const structs, string fields with the project's [structs] length
        rules, and clear errors for what isn't supported yet. Also Task 15.9 (printing an
        array) and 15.10 (an interpolated string outside print) now give clear errors.
18.2.2: named arguments for function calls and struct construction - any order, positional
        first, any defaulted parameter skippable, evaluated left to right as written.
18.2.3: nesting - structs in structs (with the [structs] depth limits), fixed-size array
        fields, arrays of structs; array and struct fields start with their own defaults.
        Also: string arrays declared without a value now start as "" instead of NULL.
"""

import pytest

from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import StructDecl, StructType, MemberExpr
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from src.config import StructsConfig
from tests.test_end_to_end import compile_and_run


def parse(source: str):
    return Parser(Lexer(source, "test.fusion").tokenize()).parse_program()


def analyze(source: str, config: StructsConfig = None):
    """Run semantic analysis; return (analyzer, ast, ok)."""
    ast = parse(source)
    analyzer = SemanticAnalyzer(structs_config=config)
    ok = analyzer.analyze(ast)
    return analyzer, ast, ok


def errors_of(source: str, config: StructsConfig = None) -> str:
    analyzer, _, ok = analyze(source, config)
    assert not ok, "expected semantic errors"
    return "\n".join(str(e) for e in analyzer.get_errors())


def warnings_of(source: str, config: StructsConfig = None) -> str:
    analyzer, _, ok = analyze(source, config)
    assert ok, analyzer.get_errors()
    return "\n".join(str(w) for w in analyzer.get_warnings())


def generate_c(source: str, config: StructsConfig = None) -> str:
    analyzer, ast, ok = analyze(source, config)
    assert ok, analyzer.get_errors()
    return CCodeGenerator().generate(ast)


POINT = 'struct Point\n    int x\n    int y\n\n'


def main(body: str) -> str:
    """Wrap indented statements in `void function main()`."""
    return 'void function main()\n' + ''.join(f'    {line}\n' for line in body.splitlines())


# ============================================================
# Parsing
# ============================================================

@pytest.mark.parametrize("source", [
    'struct Point\n    int x\n    int y\n',
    'struct Point {\n    int x\n    int y\n}\n',
    'struct Point\n    int x\n    int y\nEnd struct\n',
])
def test_three_block_styles(source):
    struct = parse(source).declarations[0]
    assert isinstance(struct, StructDecl)
    assert struct.name == 'Point'
    assert [f.name for f in struct.fields] == ['x', 'y']


def test_field_default_parsed():
    struct = parse('struct Player\n    string name\n    float health = 100.0\n').declarations[0]
    assert struct.fields[0].default_value is None
    assert struct.fields[1].default_value.value == 100.0


@pytest.mark.parametrize("member", [
    '    int function length() : 0\n',
    '    constructor(int x)\n',
    '    int size()\n',
])
def test_functions_inside_struct_rejected(member):
    with pytest.raises(ParserError) as exc:
        parse('struct Point\n    int x\n' + member)
    assert 'only contain fields' in str(exc.value)


def test_field_access_chain_parses():
    ast = parse(POINT + main('Point p\nint a = p.x'))
    initializer = ast.declarations[1].body.statements[1].initializer
    assert isinstance(initializer, MemberExpr) and initializer.member == 'x'


def test_struct_variable_declaration_parses():
    ast = parse(POINT + main('Point p'))
    assert isinstance(ast.declarations[1].body.statements[0].var_type, StructType)


# ============================================================
# Code generation
# ============================================================

def test_struct_typedef_emitted_before_functions():
    c_code = generate_c(POINT + main('Point p = Point(3, 4)'))
    assert 'typedef struct Point {\n    int x;\n    int y;\n} Point;' in c_code
    assert c_code.index('typedef struct Point') < c_code.index('// Forward declarations')


def test_constructor_becomes_compound_literal():
    assert 'Point p = (Point){3, 4};' in generate_c(POINT + main('Point p = Point(3, 4)'))


def test_uninitialized_struct_gets_zero_and_defaults():
    c_code = generate_c(
        'struct Player\n    string name\n    float health = 100.0\n    bool alive\n    char tag\n\n'
        + main('Player p')
    )
    assert "Player p = (Player){\"\", 100.0f, false, '\\0'};" in c_code


def test_omitted_trailing_defaults_filled_in():
    c_code = generate_c(
        'struct Book\n    string title\n    bool available = true\n\n' + main('Book b = Book("Dune")')
    )
    assert 'Book b = (Book){"Dune", true};' in c_code


def test_field_access_and_assignment():
    c_code = generate_c(POINT + main('Point p\np.x = 5\nint y = p.x + 1'))
    assert 'p.x = 5;' in c_code
    assert 'int y = (p.x + 1);' in c_code


def test_struct_parameters_and_return_values():
    c_code = generate_c(
        POINT + 'Point function add(Point a, Point b)\n    return Point(a.x + b.x, a.y + b.y)\n'
        + main('Point c = add(Point(1, 2), Point(3, 4))')
    )
    assert 'Point add(Point a, Point b);' in c_code
    assert 'return (Point){(a.x + b.x), (a.y + b.y)};' in c_code


def test_const_struct():
    assert 'const Point ORIGIN = (Point){0, 0};' in generate_c(
        POINT + main('const Point ORIGIN = Point(0, 0)\nint x = ORIGIN.x'))


def test_c_keyword_struct_and_field_names_mangled():
    c_code = generate_c('struct union\n    int register\n\n' + main('union u\nu.register = 1'))
    assert 'typedef struct fusion_union {' in c_code
    assert 'int fusion_register;' in c_code
    assert 'u.fusion_register = 1;' in c_code


def test_struct_declared_after_use():
    _, _, ok = analyze(
        'Point function origin()\n    return Point(0, 0)\n' + main('Point p = origin()') + '\n' + POINT)
    assert ok


def test_struct_in_function_type():
    _, _, ok = analyze(
        POINT + 'int function getx(Point p) : p.x\n'
        + main('(Point) : int f = getx\nint v = f(Point(1, 2))'))
    assert ok


def test_interpolating_fields():
    c_code = generate_c(POINT + main('Point p\nprint("({p.x}, {p.y})")'))
    assert 'printf("(%d, %d)\\n", p.x, p.y);' in c_code


# ============================================================
# Errors
# ============================================================

@pytest.mark.parametrize("source, message", [
    (main('Shape s'), "Unknown type 'Shape'"),
    ('int function f(Shape s) : 0\n' + main('int x = 1'), "Unknown type 'Shape'"),
    ('Shape function f()\n    return\n' + main('int x = 1'), "Unknown type 'Shape'"),
    (POINT + 'int function Point() : 1\n' + main('int x = 1'), "Duplicate declaration of 'Point'"),
    ('struct print\n    int x\n\n' + main('int x = 1'), "Duplicate declaration of 'print'"),
    ('struct Empty {\n}\n' + main('int x = 1'), "has no fields"),
    ('struct P\n    int x\n    float x\n\n' + main('int y = 1'), "two fields named 'x'"),
    ('struct P\n    void x\n\n' + main('int y = 1'), "can't be void"),
    ('struct P\n    (int) : int f\n\n' + main('int y = 1'), "can't hold a function"),
    ('struct P\n    int x = y\n\n' + main('int y = 1'), "must be a constant"),
    ('struct P\n    int x = "no"\n\n' + main('int y = 1'), "expected int, got string"),
])
def test_declaration_errors(source, message):
    assert message in errors_of(source)


@pytest.mark.parametrize("body, message", [
    ('Point p = Point(1)', "Struct 'Point' expects 2 argument(s) (one per field, in order: x, y), got 1"),
    ('Point p = Point(1, 2, 3)', "expects 2 argument(s)"),
    ('Point p = Point(1, "two")', "Argument 2 to 'Point' (field 'y'): expected int, got string"),
    ('Point p\nint z = p.z', "Struct 'Point' has no field 'z' (its fields: x, y)"),
    ('int n = 5\nint z = n.x', "Cannot read field 'x' of a value of type int"),
    ('Point p\nPoint q\nbool same = p == q', "Comparing structs with '==' is not supported yet"),
    ('Point p\nPoint q\nbool diff = p != q', "Comparing structs with '!=' is not supported yet"),
    ('Point p\nPoint q = p + p', "must be numeric, got Point"),
    ('Point p\nprint("{p}")', "Can't print a whole Point value"),
    ('Point p\nprint(p)', "expected string, got Point"),
    ('const Point O = Point(0, 0)\nO.x = 1', "Cannot assign to field 'x' of constant 'O'"),
    ('Point p\np.x = "text"', "Cannot assign string to field 'x' of type int"),
    ('Point p = Point', "'Point' is a struct type, not a value"),
    ('int Point = 1', "Variable 'Point' has the same name as struct 'Point'"),
])
def test_usage_errors(body, message):
    assert message in errors_of(POINT + main(body))


def test_parameter_named_like_struct_rejected():
    assert "Parameter 'Point' has the same name as struct 'Point'" in errors_of(
        POINT + 'int function f(int Point) : Point\n' + main('int x = f(1)'))


def test_assigning_field_of_call_result_rejected():
    assert "Can only assign to field 'x' of a struct stored in a variable" in errors_of(
        POINT + 'Point function make() : Point(1, 2)\n' + main('make().x = 5'))


def test_default_in_middle_makes_earlier_fields_required():
    # `level` has a default but `name` after it doesn't - positionally, both must be given
    source = 'struct P\n    int level = 1\n    string name\n\n'
    assert "expects 2 argument(s)" in errors_of(source + main('P p = P(5)'))
    assert analyze(source + main('P p = P(5, "x")'))[2]


def test_arithmetic_on_non_numbers_is_an_error_not_a_crash():
    """Found during 18.2.1: `PrimitiveType('void', location=...)` passed 'void' as the
    location, so any arithmetic on a non-number crashed the compiler with a TypeError."""
    assert "must be numeric, got int[2]" in errors_of(main('int[] a = [1, 2]\nint b = a + 1'))


def test_printing_an_array_is_a_clear_error_not_a_crash():
    """Task 15.9 - used to crash the code generator."""
    assert "Can't print a whole int[3] value" in errors_of(main('int[] a = [1, 2, 3]\nprint("{a}")'))


def test_interpolated_string_outside_print_rejected():
    """Task 15.10 - `string s = "x is {x}"` used to pass, then generate invalid C."""
    message = errors_of(main('int x = 5\nstring s = "x is {x}"'))
    assert "can only be passed directly to print()" in message


# ============================================================
# String fields - [structs] settings in fusion.toml
# ============================================================

BOOK = 'struct Book\n    string title\n\n'


def test_short_string_no_warning():
    assert warnings_of(BOOK + main('Book b = Book("Dune")')) == ''


def test_long_string_kept_in_full_with_warning():
    text = 'x' * 210
    source = BOOK + main(f'Book b = Book("{text}")')
    assert "has 210 characters (the project's string_warn_length guideline is 64) - kept in full" \
        in warnings_of(source)
    assert f'"{text}"' in generate_c(source)


def test_string_over_max_length_is_cut_with_warning():
    source = BOOK + main(f'Book b = Book("{"y" * 5000}")')
    assert "has 5000 characters - cut to the project's string_max_length of 4096" in warnings_of(source)
    c_code = generate_c(source)
    assert f'"{"y" * 4096}"' in c_code and "y" * 4097 not in c_code


def test_custom_lengths():
    config = StructsConfig(string_warn_length=5, string_max_length=8)
    source = BOOK + main('Book b = Book("123456")\nb.title = "123456789"')
    warnings = warnings_of(source, config)
    assert "has 6 characters (the project's string_warn_length guideline is 5)" in warnings
    assert "has 9 characters - cut to the project's string_max_length of 8" in warnings
    assert 'b.title = "12345678";' in generate_c(source, config)


def test_warn_length_zero_never_warns():
    assert warnings_of(BOOK + main(f'Book b = Book("{"z" * 300}")'),
                       StructsConfig(string_warn_length=0)) == ''


def test_string_default_follows_length_rules():
    source = f'struct Book\n    string title = "{"d" * 100}"\n\n' + main('Book b')
    assert "has 100 characters" in warnings_of(source)


def test_max_memory_means_no_cut_and_an_unsafe_warning():
    config = StructsConfig(string_max_length=None)
    source = BOOK + main(f'Book b = Book("{"m" * 5000}")')
    warnings = warnings_of(source, config)
    assert 'Unsafe setting' in warnings and '"max memory"' in warnings
    assert f'"{"m" * 5000}"' in generate_c(source, config)


def test_immutable_string_fields():
    config = StructsConfig(string_mutable=False)
    assert "can't be changed after the struct is created" in errors_of(
        BOOK + main('Book b = Book("a")\nb.title = "b"'), config)
    # Construction is still fine
    assert analyze(BOOK + main('Book b = Book("a")'), config)[2]


def test_pooled_storage_not_implemented_yet():
    assert 'string_storage = "pooled", which is not implemented yet (Task 17)' in errors_of(
        BOOK + main('Book b = Book("a")'), StructsConfig(string_storage='pooled'))


# ============================================================
# 18.2.2 - Named arguments (function calls and struct construction)
# ============================================================

SUB = 'int function sub(int a, int b) : a - b\n'
SHIP = ('void function createShip(string name = "Unnamed", float speed = 100.0, int crew = 50)\n'
        '    print("{name} {speed} {crew}")\n')
NEXT = ('int function next(int[] counter)\n'
        '    counter[0] = counter[0] + 1\n'
        '    return counter[0]\n')


def test_named_arguments_parse():
    ast = parse(SUB + main('int r = sub(b = 5, a = 3)'))
    call = ast.declarations[1].body.statements[0].initializer
    assert [type(a).__name__ for a in call.arguments] == ['NamedArgument', 'NamedArgument']
    assert [a.name for a in call.arguments] == ['b', 'a']


def test_named_arguments_reordered_to_parameter_order():
    assert 'int r = sub(3, 5);' in generate_c(SUB + main('int r = sub(b = 5, a = 3)'))


def test_named_argument_skips_any_defaulted_parameter():
    c_code = generate_c(SHIP + main('createShip(crew = 200)'))
    assert 'createShip("Unnamed", 100.0f, 200);' in c_code


def test_positional_then_named():
    c_code = generate_c(SHIP + main('createShip("Discovery", crew = 80, speed = 150.0)'))
    assert 'createShip("Discovery", 150.0f, 80);' in c_code


def test_named_struct_construction():
    assert 'Point p = (Point){3, 4};' in generate_c(POINT + main('Point p = Point(y = 4, x = 3)'))


def test_named_struct_construction_with_defaults():
    source = ('struct Ship\n    string name = "Unnamed"\n    float speed = 100.0\n    int crew = 50\n\n'
              + main('Ship s = Ship(crew = 7)'))
    assert 'Ship s = (Ship){"Unnamed", 100.0f, 7};' in generate_c(source)


def test_named_struct_field_string_rules_apply():
    source = BOOK + main(f'Book b = Book(title = "{"n" * 100}")')
    assert "has 100 characters" in warnings_of(source)


def test_named_arguments_without_calls_need_no_temporaries():
    assert 'fusion_arg' not in generate_c(SUB + main('int x = 1\nint r = sub(b = x, a = 3)'))


def test_reordered_calls_use_temporaries_in_written_order():
    c_code = generate_c(NEXT + SUB + main('int[] c = [0]\nint d = sub(b = next(c), a = next(c))'))
    assert 'int fusion_arg_1;' in c_code and 'int fusion_arg_2;' in c_code
    assert ('int d = (fusion_arg_1 = next(c, 1), fusion_arg_2 = next(c, 1), '
            'sub(fusion_arg_2, fusion_arg_1));') in c_code


def test_temporaries_in_a_lambda_are_declared_in_the_lambda():
    c_code = generate_c(
        SUB + 'int function twice(int v) : v * 2\n'
        + main('(int) : int f = func(int x) : sub(b = twice(x), a = twice(x + 1))\nint r = f(3)'))
    lambda_code = c_code[c_code.index('static int fusion_lambda_1'):]
    lambda_code = lambda_code[:lambda_code.index('}')]
    assert 'int fusion_arg_1;' in lambda_code


@pytest.mark.parametrize("body, message", [
    ('int r = sub(a = 1, 2)',
     "Argument 2 to 'sub' has no name but comes after a named argument"),
    ('int r = sub(a = 1, c = 2)', "'sub' has no parameter named 'c' (its parameters: a, b)"),
    ('int r = sub(a = 1, a = 2)', "Parameter 'a' of 'sub' is given twice"),
    ('int r = sub(1, 2, b = 3)', "Parameter 'b' of 'sub' is given twice (by position and by name)"),
    ('int r = sub(b = 2)', "Missing argument for parameter 'a' of 'sub'"),
    ('int r = sub(a = 1, b = "x")', "Argument 'b' to 'sub': expected int, got string"),
    ('(int, int) : int f = sub\nint r = f(a = 1, b = 2)',
     "Named argument 'a' can't be used when calling 'f' (a function variable)"),
    ('print(message = "hi")', "Named argument 'message' can't be used when calling built-in function 'print'"),
    ('int r = (func(int a) : a)(a = 1)', "Named argument 'a' can't be used when calling a function value"),
])
def test_named_argument_errors(body, message):
    assert message in errors_of(SUB + main(body))


def test_unknown_name_does_not_also_report_missing():
    message = errors_of(SUB + main('int r = sub(a = 1, c = 2)'))
    assert "Missing argument" not in message


def test_every_missing_argument_is_reported():
    message = errors_of('int function f(int a, int b, int c) : a\n' + main('int r = f(b = 1)'))
    assert "Missing argument for parameter 'a'" in message
    assert "Missing argument for parameter 'c'" in message


@pytest.mark.parametrize("body, message", [
    ('Point p = Point(x = 1)', "Missing argument for field 'y' of struct 'Point'"),
    ('Point p = Point(z = 1, x = 1, y = 2)', "Struct 'Point' has no field named 'z' (its fields: x, y)"),
    ('Point p = Point(1, x = 2)', "Field 'x' of struct 'Point' is given twice (by position and by name)"),
])
def test_named_construction_errors(body, message):
    assert message in errors_of(POINT + main(body))


def test_named_arguments_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        POINT + SUB + SHIP + NEXT + main(
            'int r = sub(b = 5, a = 3)\n'
            'print("{r}")\n'
            'createShip(crew = 200)\n'
            'createShip("Discovery", crew = 80, speed = 150.0)\n'
            'Point p = Point(y = 4, x = 3)\n'
            'print("{p.x} {p.y}")\n'
            'int[] c = [0]\n'
            'int d = sub(b = next(c), a = next(c))\n'
            'print("{d}")\n'
            'Point q = Point(y = next(c), x = next(c))\n'
            'print("{q.x} {q.y}")\n'
        )
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == [
        "-2",
        "Unnamed 100.000000 200",
        "Discovery 150.000000 80",
        "3 4",
        "1",       # b = next() runs first (1), then a = next() (2): 2 - 1
        "4 3",     # y = next() runs first (3), then x = next() (4)
    ]


# ============================================================
# 18.2.3 - Nesting: structs in structs, array fields, arrays of structs
# ============================================================

LINE = 'struct Line\n    Point a\n    Point b\n\n'
SHAPE = 'struct Shape\n    Line[2] edges\n\n'
SCENE = 'struct Scene\n    Shape s\n\n'
SCORES = 'struct Player\n    string name\n    int[3] scores\n    string[2] tags\n\n'


def test_nested_struct_typedefs_in_dependency_order():
    # Line is declared before Point in the source, but C needs Point first
    c_code = generate_c(LINE + POINT + main('Line l'))
    assert c_code.index('typedef struct Point') < c_code.index('typedef struct Line')
    assert '    Point a;' in c_code


def test_array_fields_are_c_arrays():
    c_code = generate_c(SCORES + main('Player p'))
    assert '    int scores[3];' in c_code
    assert '    char* tags[2];' in c_code


def test_nested_field_access_and_assignment():
    c_code = generate_c(POINT + LINE + main('Line l\nl.a.x = 5\nint y = l.b.y'))
    assert 'l.a.x = 5;' in c_code
    assert 'int y = l.b.y;' in c_code


def test_nested_defaults_and_empty_strings():
    c_code = generate_c(POINT + 'struct Box\n    Point corner\n    string label = "box"\n\n'
                        + SCORES + main('Box b\nPlayer p'))
    assert 'Box b = (Box){(Point){0, 0}, "box"};' in c_code
    assert 'Player p = (Player){"", {0}, {"", ""}};' in c_code


def test_array_and_struct_fields_can_be_left_out_of_constructor():
    c_code = generate_c(SCORES + main('Player p = Player("Ada")'))
    assert 'Player p = (Player){"Ada", {0}, {"", ""}};' in c_code


def test_array_field_from_literal():
    c_code = generate_c(SCORES + main('Player p = Player("Ada", [1, 2, 3])'))
    assert '(Player){"Ada", {1, 2, 3}, {"", ""}}' in c_code


def test_named_construction_with_nested_struct():
    c_code = generate_c(POINT + LINE + main('Line l = Line(b = Point(5, 5))'))
    assert 'Line l = (Line){(Point){0, 0}, (Point){5, 5}};' in c_code


def test_array_of_structs_zeroed_with_nested_braces():
    assert 'Point pts[3] = {{0}};' in generate_c(POINT + main('Point[3] pts'))


def test_array_of_structs_from_literal_and_element_access():
    c_code = generate_c(POINT + main('Point[] pts = [Point(1, 2), Point(3, 4)]\npts[0].x = 7'))
    assert 'Point pts[2] = {(Point){1, 2}, (Point){3, 4}};' in c_code
    assert 'pts[0].x = 7;' in c_code


def test_array_of_structs_parameter():
    c_code = generate_c(POINT + 'void function shift(Point[] pts)\n    pts[0].x = 1\n'
                        + main('Point[2] ps\nshift(ps)'))
    assert 'void shift(Point* pts, int fusion_len_pts);' in c_code
    assert 'shift(ps, 2);' in c_code


def test_array_field_passed_to_array_parameter():
    c_code = generate_c(SCORES + 'int function first(int[] v) : v[0]\n'
                        + main('Player p\nint f = first(p.scores)\nint n = len(p.scores)'))
    assert 'first(p.scores, 3)' in c_code
    assert 'int n = 3;' in c_code


def test_string_array_variable_starts_with_empty_strings():
    """Found during 18.2.3: `string[2] names` left NULL pointers (printed "(null)", or
    crashes on other C runtimes)."""
    assert 'char* names[2] = {"", ""};' in generate_c(main('string[2] names'))


def test_large_string_array_filled_in_a_loop():
    c_code = generate_c(main('string[100] names'))
    assert 'for (int fusion_i = 0; fusion_i < 100; fusion_i++) {' in c_code
    assert 'names[fusion_i] = "";' in c_code


# --- Depth limits ([structs] in fusion.toml) and cycles

def test_depth_three_warns_by_default():
    warnings = warnings_of(POINT + LINE + SHAPE + main('int y = 1'))
    assert "Struct 'Shape' is nested 3 levels deep (Shape -> Line -> Point) - the project warns " \
           "from 3 levels" in warnings


def test_depth_two_has_no_warning_by_default():
    assert warnings_of(POINT + LINE + main('int y = 1')) == ''


def test_depth_four_is_an_error_by_default():
    message = errors_of(POINT + LINE + SHAPE + SCENE + main('int y = 1'))
    assert "Struct 'Scene' is nested 4 levels deep (Scene -> Shape -> Line -> Point) - the " \
           "project allows 3" in message


def test_max_depth_one_turns_off_nested_structs():
    message = errors_of(POINT + LINE + main('int y = 1'), StructsConfig(max_nesting_depth=1))
    assert "Struct 'Line' is nested 2 levels deep (Line -> Point) - the project allows 1" in message


def test_raising_the_max_allows_deeper_structs():
    assert analyze(POINT + LINE + SHAPE + SCENE + main('int y = 1'),
                   StructsConfig(max_nesting_depth=4))[2]


def test_warn_depth_zero_never_warns():
    assert warnings_of(POINT + LINE + SHAPE + main('int y = 1'),
                       StructsConfig(warn_nesting_depth=0)) == ''


def test_depth_error_reported_once_where_it_starts():
    source = POINT + LINE + SHAPE + SCENE + 'struct World\n    Scene sc\n\n' + main('int y = 1')
    message = errors_of(source)
    assert "Struct 'Scene' is nested 4" in message
    assert "Struct 'World'" not in message


@pytest.mark.parametrize("source, message", [
    ('struct A\n    B b\n\nstruct B\n    A a\n\n', "Struct 'A' contains itself (A -> B -> A)"),
    ('struct A\n    A[2] kids\n\n', "Struct 'A' contains itself (A -> A)"),
])
def test_struct_containing_itself_rejected(source, message):
    assert message in errors_of(source + main('int y = 1'))


# --- Errors

@pytest.mark.parametrize("source, message", [
    ('struct P\n    int[] xs\n\n' + main('int y = 1'), "Array field 'xs' of struct 'P' needs a size"),
    ('struct P\n    void[2] xs\n\n' + main('int y = 1'), "can't hold void"),
    (POINT + 'struct Q\n    Point p = 5\n\n' + main('int y = 1'),
     "Field 'p' of struct 'Q' can't have a default value - an array or struct field"),
    ('struct P\n    int[3] xs\n\n' + main('int[3] a = [1, 2, 3]\nP p = P(a)'),
     "Field 'xs' of struct 'P': needs an array literal here"),
    ('struct P\n    int[3] xs\n\n' + main('P p = P([1, 2])'),
     "Field 'xs' of struct 'P': expected 3 element(s), got 2"),
    ('struct P\n    int[3] xs\n\n' + main('P p = P(xs = ["a", "b", "c"])'),
     "expected elements of type int, got string"),
    ('struct P\n    int[3] xs\n\n' + main('P p\np.xs = [1, 2, 3]'),
     "Cannot assign array field 'xs' as a whole"),
    ('struct P\n    int[3] xs\n\n' + main('const P c = P([1, 2, 3])\nc.xs[0] = 5'),
     "Cannot assign to an element of an array inside constant 'c'"),
    ('struct P\n    int[3] xs\n\nvoid function z(int[] v)\n    v[0] = 0\n'
     + main('const P c = P([1, 2, 3])\nz(c.xs)'), "an array inside const 'c' can't be passed"),
    (POINT + LINE + main('const Line k = Line(Point(1, 1), Point(2, 2))\nk.a.x = 5'),
     "Cannot assign to field 'x' of constant 'k'"),
    (POINT + main('const Point[] P = [Point(1, 1)]\nP[0].x = 5'),
     "Cannot assign to field 'x' of constant 'P'"),
    (POINT + LINE + main('Line l\nprint("{l.a}")'), "Can't print a whole Point value"),
])
def test_nesting_errors(source, message):
    assert message in errors_of(source)


def test_struct_field_default_reports_one_error():
    message = errors_of(POINT + 'struct Q\n    Point p = 5\n\n' + main('int y = 1'))
    assert "expected Point, got int" not in message


def test_nesting_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        POINT + LINE + SCORES +
        'struct Path\n    Point[3] stops\n\n'
        'int function total(int[] values)\n'
        '    int sum = 0\n'
        '    for i in range(0, len(values))\n'
        '        sum = sum + values[i]\n'
        '    return sum\n'
        'void function shift(Point[] pts)\n'
        '    for i in range(0, len(pts))\n'
        '        pts[i].x = pts[i].x + 10\n'
        + main(
            'Line l = Line(Point(1, 2), Point(3, 4))\n'
            'l.a.x = 9\n'
            'Line copy = l\n'
            'copy.b.y = 100\n'
            'print("{@1} {@2} {@3} {@4}", l.a.x, l.a.y, l.b.y, copy.b.y)\n'
            'Player p = Player("Ada", [10, 20, 30])\n'
            'p.scores[1] = 25\n'
            'Player q = p\n'
            'q.scores[0] = 0\n'
            'print("{@1} {@2} {@3} [{@4}]", total(p.scores), len(p.scores), p.scores[0], p.tags[0])\n'
            'print("{@1}", q.scores[0])\n'
            'Point[] more = [Point(1, 1), Point(2, 2)]\n'
            'shift(more)\n'
            'Path path\n'
            'path.stops[2].x = 7\n'
            'print("{@1} {@2} {@3}", more[0].x, more[1].x, path.stops[2].x)\n'
            'string[2] names\n'
            'print("[{@1}][{@2}]", names[0], names[1])\n'
        )
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == ["9 2 4 100", "65 3 10 []", "0", "11 12 7", "[][]"]


# ============================================================
# End to end (GCC)
# ============================================================

def test_structs_end_to_end():
    exit_code, stdout, stderr = compile_and_run(
        POINT +
        'struct Player {\n    string name\n    float health = 100.0\n    int score\n}\n'
        'Point function add(Point a, Point b)\n    return Point(a.x + b.x, a.y + b.y)\n'
        'void function clobber(Point p)\n    p.x = 999\n    print("inside: {p.x}")\n'
        + main(
            'Point a = Point(3, 4)\n'
            'Point b = a\n'
            'b.x = 9\n'
            'print("{a.x} {a.y} {b.x} {b.y}")\n'
            'Point c = add(a, b)\n'
            'print("{c.x} {c.y}")\n'
            'clobber(a)\n'
            'print("after: {a.x}")\n'
            'Player p = Player("Ada", 75, 10)\n'
            'p.score = p.score + 5\n'
            'p.name = "Grace"\n'
            'print("{p.name} {p.score}")\n'
            'Player q\n'
            'print("[{q.name}] {q.score}")\n'
        )
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == [
        "3 4 9 4", "12 8", "inside: 999", "after: 3", "Grace 15", "[] 0",
    ]
