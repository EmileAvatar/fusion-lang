"""Tests for Task 18.2 - structs.

18.2.1: core structs - declaration (three block styles), generated positional constructor,
        field defaults, `.` field access and assignment, value semantics (copy on assign,
        pass and return), const structs, string fields with the project's [structs] length
        rules, and clear errors for what isn't supported yet. Also Task 15.9 (printing an
        array) and 15.10 (an interpolated string outside print) now give clear errors.
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
    ('struct P\n    int[3] xs\n\n' + main('int y = 1'), "array fields are not supported yet"),
    (POINT + 'struct Line\n    Point a\n\n' + main('int y = 1'), "struct inside a struct is not supported yet"),
    (POINT + main('Point[2] ps'), "Arrays of structs (Point[]) are not supported yet"),
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
