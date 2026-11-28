"""Task 47.3 - an enum as a built-in value struct (D.188-D.194, files/Value_Structs.md).

    enum Planet
        MERCURY(0.3303, 2439.7, "Mercury")           // id 0
        EARTH(5.976, 6378.14, "Earth"), 200          // id written at the back
        201, MARS(0.6421, 3397.2, "Mars")            // or at the front
        public const double mass                     // Planet.EARTH.mass, p.mass - never set
        double function gravity(double kg) ...       // a method
        string function toString() : name            // printing shows Earth

Each value is a static const struct (never on the heap); a variable borrows it. Every program runs under the leak
check.
"""
import pytest

from src.config.project_config import EnumsConfig, load_project_config, ProjectConfigError
from src.semantic import SemanticAnalyzer
from tests.test_end_to_end import compile_and_run
from tests.test_structs import parse

PLANET = '''enum Planet
    MERCURY(0.3303, 2439.7, "Mercury")
    EARTH(5.976, 6378.14, "Earth"), 200
    201, MARS(0.6421, 3397.2, "Mars")

    public const double mass
    public const double radius
    public const string name

    double function gravity(double kg)
        return 0.0000000000667 * mass * 1000000000000000000000000.0 * kg / (radius * radius * 1000000.0)

    string function toString()
        return name

'''


def source_of(body: str, top: str = PLANET) -> str:
    return top + 'void function main()\n' + ''.join(f'    {line}\n' for line in body.split('\n'))


def run(body: str, top: str = PLANET, expect_fail: bool = False) -> list:
    code, out, err = compile_and_run(source_of(body, top))
    assert (code != 0) == expect_fail, out + err
    return [line.strip() for line in (out + err).strip().splitlines() if not line.startswith('[freed')]


def analyzed(body: str, top: str = PLANET, upper: str = 'false'):
    analyzer = SemanticAnalyzer(enums_config=EnumsConfig(upper_case_names=upper))
    analyzer.analyze(parse(source_of(body, top)))
    return [e.message for e in analyzer.get_errors()], [w.message for w in analyzer.get_warnings()]


def errors_of(body: str, top: str = PLANET) -> list:
    return analyzed(body, top)[0]


# ---- fields, ids, toString ----

def test_fields_read_without_a_variable():
    assert run('print("{@1} {@2}", Planet.EARTH.mass, Planet.MARS.radius)') == ['5.976000 3397.200000']


def test_a_variable_borrows_a_value():
    assert run('Planet p = Planet.MARS\nprint("{p} {@1} {@2} {@3}", p.name, p.value(), p.id)\nprint("{@1}", p.enumTypeName)') \
        == ['Mars Mars 201 201', 'MARS']


def test_ids_counted_written_front_and_back():
    assert run('for each in Planet.values()\n    print("{@1} {@2}", each.enumTypeName, each.value())') == [
        'MERCURY 0', 'EARTH 200', 'MARS 201']


def test_the_count_skips_an_id_written_later():
    top = 'enum Code\n    A\n    B\n    1, C\n\n'
    assert run('print("{@1} {@2} {@3}", Code.A.value(), Code.B.value(), Code.C.value())', top) == ['0 2 1']


def test_two_values_with_one_id():
    found = errors_of('print("x")', 'enum Code\n    1, A\n    B, 1\n\n')
    assert any("both have the value 1" in e for e in found), found


def test_a_status_enum_of_ids():
    top = 'enum Status\n    200, OK\n    403, ERROR\n    500, SERVER_ERROR\n\n'
    assert run('print("{@1} {@2} {@3}", Status.OK, Status.OK.value(), Status.fromValue(403))\nprint(toString(Status.SERVER_ERROR.id))',
               top) == ['OK 200 ERROR', '500']


def test_from_value_unknown_is_an_error():
    top = 'enum Status\n    200, OK\n\n'
    lines = run('int n = 999\nStatus s = Status.fromValue(n)\nprint("{s}")', top, expect_fail=True)
    assert any('999 is not an id of enum Status' in line for line in lines), lines


def test_to_string_by_default_is_the_name():
    top = 'enum Planet\n    EARTH(5.976)\n\n    public const double mass\n\n'
    assert run('print("{@1}", Planet.EARTH)\nPlanet p = Planet.EARTH\nprint("{p} {@1}", toString(p))', top) == ['EARTH', 'EARTH EARTH']


def test_to_string_with_text_worked_out():
    top = ('enum Planet\n    EARTH(3, "Earth")\n\n    public const int order\n    public const string name\n\n'
           '    string function toString()\n        return "{name} ({enumTypeName}, {order})"\n\n')
    assert run('print("{@1}", Planet.EARTH)', top) == ['Earth (EARTH, 3)']


def test_a_method_and_a_value_in_a_struct_and_list():
    assert run('print("{@1}", Planet.EARTH.gravity(80.0) > 700.0)\nList<Planet> all = Planet.values()\ndouble total = 0.0\n'
               'for p in all\n    total = total + p.mass\nprint("{@1}", total > 6.9)') == ['true', 'true']


def test_named_values_and_defaults():
    top = ('enum Planet\n    EARTH(5.976, 6378.14)\n    VENUS(radius = 6051.8, mass = 4.869, name = "Venus")\n\n'
           '    public const double mass\n    public const double radius\n    public const string name = "?"\n\n')
    assert run('print("{@1} {@2} {@3}", Planet.EARTH.name, Planet.VENUS.name, Planet.VENUS.radius)', top) == ['? Venus 6051.800000']


def test_a_constructor_with_a_calculation():
    top = ('const double SCALE = 1000.0\n'
           'enum Planet\n    EARTH(5.976, 6378.14, "Earth")\n\n'
           '    public const double massTonnes\n    public const double radius\n    public const string label\n\n'
           '    private Enum(double m, double r, string n)\n        this.massTonnes = m * SCALE\n'
           '        this.radius = r\n        label = "Planet " + n\n\n')
    assert run('print("{@1} {@2}", Planet.EARTH.massTonnes, Planet.EARTH.label)', top) == ['5976.000000 Planet Earth']


def test_const_static_before_enum():
    top = 'const static enum Level\n    LOW(1)\n    HIGH(9)\n\n    public const int weight\n\n'
    assert run('print("{@1}", Level.HIGH.weight)', top) == ['9']


def test_every_field_type():
    top = ('enum Thing\n    ONE(true, \'x\', 7, 300, 100000, 10000000000, 99999999999999999999999, 1.5, 2.5, "t")\n\n'
           '    public const bool b\n    public const char c\n    public const byte y\n    public const short s\n'
           '    public const int i\n    public const long l\n    public const int128 w\n    public const float f\n'
           '    public const double d\n    public const string t\n\n')
    assert run('print("{@1} {@2} {@3} {@4} {@5}", Thing.ONE.b, Thing.ONE.c, Thing.ONE.y, Thing.ONE.s, Thing.ONE.i)\n'
               'print("{@1} {@2} {@3} {@4} {@5}", Thing.ONE.l, Thing.ONE.w, Thing.ONE.f, Thing.ONE.d, Thing.ONE.t)', top) == [
        'true x 7 300 100000', '10000000000 99999999999999999999999 1.500000 2.500000 t']


def test_a_null_enum_has_no_fields():
    assert run('Planet nobody\ntry\n    print("{@1}", nobody.mass)\ncatch NullError e\n    print("caught")') == ['caught']


# ---- an enum without fields: a const fixed array per value ----

PRIMES = 'enum Primes\n    SMALL(2, 3, 5)\n    BIG(101, 103)\n\n'


def test_items_of_a_value():
    assert run('print("{@1} {@2}", Primes.SMALL[1], Primes.BIG[0])\nPrimes q = Primes.SMALL\nprint("{@1}", q[2])', PRIMES) == ['3 101', '5']


def test_an_item_past_the_end():
    found = errors_of('print("{@1}", Primes.BIG[2])', PRIMES)
    assert any('BIG holds 2 item(s), 0 to 1' in e for e in found), found
    lines = run('int i = 5\nprint("{@1}", Primes.SMALL[i])', PRIMES, expect_fail=True)
    assert any('index 5 is outside the value (it holds 3)' in line for line in lines), lines


def test_items_of_mixed_types():
    found = errors_of('print("x")', 'enum Mixed\n    A(1, "x")\n\n')
    assert any('mixes' in e for e in found), found


# ---- the errors ----

@pytest.mark.parametrize('top, problem', [
    ('enum P\n    A(1.5)\n\n    public const decimal d\n\n', "can't be decimal"),
    ('enum P\n    A(1.5)\n\n    public const money m\n\n', "can't be money"),
    ('enum C: RED GREEN\nenum P\n    A(RED)\n\n    public const C color\n\n', "can't be C"),
    ('enum P\n    A(1)\n\n    public const int[] xs\n\n', "can't be"),
    ('enum P\n    A(1.5)\n\n    public const int whole\n\n', 'a int needs a whole number'),
    ('enum P\n    A(300)\n\n    public const byte b\n\n', "300 doesn't fit in a byte"),
    ('enum P\n    A(1, 2)\n\n    public const int x\n\n', 'gives 2 values'),
    ('enum P\n    A\n\n    public const int x\n\n', "doesn't give 'x'"),
    ('enum P\n    A(other = 1)\n\n    public const int x\n\n', "has no field or parameter 'other'"),
    ('int seed = 4\nenum P\n    A(seed)\n\n    public const int x\n\n', "'seed' isn't a constant"),
    ('enum P\n    A(1)\n\n    public const int id\n\n', 'every value has id and enumTypeName'),
    ('enum P\n    Circle(double r)\n    A(1)\n\n', 'mixes values carrying their own data'),
    ('enum P\n    A("a")\n\n    public const string s\n\n    string function toString()\n        string t = s\n'
     '        return t\n\n', 'gives its text in one line'),
    ('enum P\n    A(1)\n\n    public const int x\n\n    private Enum(int v)\n        print("x")\n\n',
     "only sets its fields"),
])
def test_declaration_errors(top, problem):
    found = errors_of('print("x")', top)
    assert any(problem in e for e in found), found


def test_a_field_is_never_set():
    found = errors_of('Planet.EARTH.mass = 1.0\nPlanet p = Planet.MARS\np.radius = 2.0')
    assert sum("An enum's data is fixed" in e for e in found) == 2, found


def test_a_private_field_is_read_only_inside():
    top = ('enum Planet\n    EARTH(5.976)\n\n    double mass\n\n'
           '    double function heavier(double x)\n        return mass * x\n\n')
    found = errors_of('print("{@1}", Planet.EARTH.mass)', top)
    assert any("is private - write public const double mass" in e for e in found), found
    assert run('print("{@1}", Planet.EARTH.heavier(2.0))', top) == ['11.952000']


def test_unknown_field_and_method():
    found = errors_of('print("{@1}", Planet.EARTH.weight)\nprint("{@1}", Planet.EARTH.spin())')
    assert any("has no field 'weight'" in e for e in found), found
    assert any("no method 'spin'" in e for e in found), found


# ---- [enums] upperCaseNames (D.194) ----

LOWER = 'enum Color\n    Red\n    GREEN\n\n'


@pytest.mark.parametrize('upper, errors, warnings', [('false', 0, 0), ('true', 0, 1), ('strict', 1, 0)])
def test_upper_case_names(upper, errors, warnings):
    found, warned = analyzed('print("{@1}", Color.Red)', LOWER, upper)
    assert len([e for e in found if 'capitals' in e]) == errors, found
    assert len([w for w in warned if "'Red' of enum 'Color' isn't in capitals - write RED" in w]) == warnings, warned


def test_the_setting_is_read(tmp_path):
    (tmp_path / 'settings.toml').write_text('[enums]\nupperCaseNames = "strict"\n', encoding='utf-8')
    assert load_project_config(str(tmp_path / 'main.fusion')).enums.upper_case_names == 'strict'
    (tmp_path / 'settings.toml').write_text('[enums]\nupperCaseNames = true\n', encoding='utf-8')
    assert load_project_config(str(tmp_path / 'main.fusion')).enums.upper_case_names == 'true'
    (tmp_path / 'settings.toml').write_text('[enums]\nupperCaseNames = "loud"\n', encoding='utf-8')
    with pytest.raises(ProjectConfigError):
        load_project_config(str(tmp_path / 'main.fusion'))
