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

from src.config.project_config import GenericsConfig, MemoryConfig, ProjectConfigError, _load_generics_section
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


# ---------------------------------------------------------------- 33.2b generic structs

STRUCTS = ('struct Pair<A, B>\n'
           '    A first\n'
           '    B second\n\n'
           'struct Labelled<T>\n'
           '    string label\n'
           '    T value\n\n'
           'class Car\n'
           '    public string name\n'
           '    constructor(string name)\n'
           '        this.name = name\n\n'
           'struct Garage\n'
           '    Pair<int, string> slot\n\n'
           'T function pickFirst<T, T1>(Pair<T, T1> p) : p.first\n\n')


@pytest.mark.parametrize('body, lines', [
    ('Pair<int, string> p = Pair(1, "one")\nprint("{@1} {@2}", p.first, p.second)', ['1 one']),
    ('Pair<string, string> q = Pair<string, string>("a", "b")\nq.second = "c"\nprint("{@1}{@2}", q.first, q.second)',
     ['ac']),
    ('Labelled<int> l = Labelled("n", 7)\nprint("{@1} {@2}", l.label, l.value)', ['n 7']),
    ('Pair<int, string> p = Pair(1, "one")\nPair<int, string> r = p\nprint("{@1}", r == Pair(1, "one"))', ['true']),
    ('Pair<int, string> p = Pair(1, "one")\nprint("{@1}", pickFirst(p))', ['1']),
    ('List<Pair<int, string>> pairs = [Pair(2, "two"), Pair(3, "three")]\nprint(pairs[1].second)', ['three']),
    ('Pair<Car, int> c = Pair(Car("Ada"), 3)\nprint("{@1} {@2}", c.first.name, c.second)', ['Ada 3']),
    ('Pair<Pair<int, int>, string> n = Pair(Pair(1, 2), "x")\nprint("{@1}", n.first.second)', ['2']),
    ('Garage g = Garage(Pair(5, "five"))\nprint(g.slot.second)', ['five']),
])
def test_generic_structs(body, lines):
    assert run(body, top=STRUCTS) == lines


def test_one_struct_copy_per_set_of_types():
    program = parse(STRUCTS + 'void function main()\n    Pair<int, string> a = Pair(1, "a")\n'
                              '    Pair<int, string> b = Pair(2, "b")\n    Pair<string, int> c = Pair("c", 3)\n')
    SemanticAnalyzer().analyze(program)
    names = [d.name for d in program.declarations if getattr(d, 'generic_of', None) == 'Pair']
    assert sorted(names) == ['Pair__int__string', 'Pair__string__int']


@pytest.mark.parametrize('body, message', [
    ('Pair<int> p = Pair(1, "a")', "'Pair' has 2 type parameter(s) (A, B) - 1 written"),
    ('Box<int> b', "Unknown generic type 'Box'"),
    ('Pair<int, string> p = Pair(1)', "give a value for each field (2)"),
    # the types from the left (D.171): each argument checked against them
    ('Pair<int, string> p = Pair("a", 1)', "Argument 1 to 'Pair<int, string>' (field 'first'): expected int, got string"),
])
def test_generic_struct_mistakes(body, message):
    found = errors_of(body, top=STRUCTS)
    assert any(message in e for e in found), found


# ---------------------------------------------------------------- 33.2c generic classes, methods

CLASSES = ('class Box<T>\n'
           '    T item\n'
           '    public int uses = 0\n'
           '    constructor(T item)\n'
           '        this.item = item\n'
           '    constructor(T item, int uses)\n'
           '        this(item)\n'
           '        this.uses = uses\n'
           '    T function take()\n'
           '        uses = uses + 1\n'
           '        return item\n'
           '    void function put(T x)\n'
           '        item = x\n'
           '    bool function holds(T x) : item == x\n'
           '    T function twice()\n'
           '        take()\n'
           '        return take()\n'
           '    Box<T> function copyBox() : Box(item)\n\n'
           'struct Pair<A, B>\n'
           '    A first\n'
           '    B second\n'
           '    A function left() : first\n'
           '    void function setLeft(A x)\n'
           '        first = x\n\n'
           'class Car\n'
           '    public string name\n'
           '    constructor(string name)\n'
           '        this.name = name\n\n'
           'class Shelf\n'
           '    public Box<int> box = Box(4)\n\n'
           'T function unbox(Box<T> b) : b.take()\n\n')


@pytest.mark.parametrize('body, lines', [
    ('Box<int> a = Box(5)\nint n = a.take()\na.put(7)\nprint("{@1} {@2} {@3} {@4}", n, a.take(), a.holds(7), a.uses)',
     ['5 7 true 2']),
    ('Box<string> s = Box<string>("hi")\nprint("{@1} {@2}", s.take(), unbox(s))', ['hi hi']),
    ('Box<Car> c = Box(Car("Ada"))\nprint(c.take().name)\nc.put(Car("Bo"))\nprint(c.take().name)', ['Ada', 'Bo']),
    ('Box<int> a = Box(1, 10)\nprint("{@1}", a.uses)', ['10']),
    ('Box<string> s = Box("x")\nprint("{@1} {@2}", s.twice(), s.uses)', ['x 2']),
    ('Box<int> a = Box(3)\nBox<int> b = a.copyBox()\nb.put(4)\nprint("{@1} {@2}", a.take(), b.take())', ['3 4']),
    ('List<Box<int>> boxes = [Box(1), Box(2)]\nboxes.add(Box(3))\nprint("{@1}", boxes[2].take())', ['3']),
    ('Shelf s = Shelf()\nprint("{@1}", s.box.take())', ['4']),
    ('Pair<int, string> p = Pair(1, "one")\np.setLeft(9)\nprint("{@1} {@2}", p.left(), p.second)', ['9 one']),
])
def test_generic_classes(body, lines):
    assert run(body, top=CLASSES) == lines


def test_one_class_copy_with_its_methods():
    program = parse(CLASSES + 'void function main()\n    Box<int> a = Box(1)\n    Box<int> b = Box(2)\n')
    SemanticAnalyzer().analyze(program)
    names = [d.name for d in program.declarations if d.name.startswith('Box')]
    assert 'Box__int' in names and 'Box__int.take' in names and 'Box__int.new' in names
    assert not any(n.startswith('Box.') for n in names)       # the generic's own methods aren't compiled
    assert names.count('Box__int') == 1


@pytest.mark.parametrize('body, message', [
    ('Box<int> a = Box(1)\na.put("x")', "Box<int>"),                 # named as written, not Box__int
    ('Box<int> a = Box(1)\nprint(a.item)', "Field 'item' of class 'Box<int>' is private"),
    ('Box<int> a = Box(1, 2, 3)', "give a constructor taking (1 or 2)"),
])
def test_generic_class_mistakes(body, message):
    found = errors_of(body, top=CLASSES)
    assert any(message in e for e in found), found
    assert not any('Box__' in e for e in found), found


def test_a_generic_class_with_statics_comes_later():
    found = errors_of('print("x")', top='class Box<T>\n    T item\n    static int made = 0\n\n')
    assert any("with static members comes later (Task 33.3c)" in e for e in found), found


# ---------- 33.3a a generic class with a plain parent and plain interfaces ----------

PARENTS = ('interface Printable\n    string function label()\n\n'
           'class Vehicle\n    public string name\n    constructor(string name)\n        this.name = name\n'
           '    string function kind() : "vehicle"\n\n'
           'class Car inherits Vehicle\n    constructor(string name)\n        super(name)\n'
           '    override string function kind() : "car"\n\n'
           'class Crate<T> inherits Vehicle implements Printable\n    T item\n    constructor(string name, T item)\n'
           '        super(name)\n        this.item = item\n    T function take() : item\n'
           '    override string function kind() : "crate"\n    string function label() : "crate {name}"\n\n'
           'string function describe(Vehicle v) : format("{@1} is a {@2}", v.name, v.kind())\n\n'
           'string function show(Printable p) : p.label()\n\n')


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_a_generic_class_with_a_parent_and_an_interface(ownership):
    # each copy has the parent's fields and functions, overrides them, answers the interface; is / a List of parents
    assert run('Crate<int> a = Crate("ints", 5)\nCrate<Car> b = Crate("cars", Car("mini"))\n'
               'print(describe(a))\nprint(show(b))\nprint("{@1} {@2} {@3}", a.take(), b.take().name, b.take().kind())\n'
               'List<Vehicle> all = [byVal a, byVal b, Car("van")]\nfor v in all\n    print(v.kind())\n'
               'Vehicle w = b\nif w is Crate<Car>\n    print("a crate of cars")',
               top=PARENTS, memory_config=MemoryConfig(assignment=ownership)) == [
        'ints is a crate', 'crate cars', '5 mini car', 'crate', 'crate', 'car', 'a crate of cars']


def test_a_generic_class_missing_an_interface_function():
    found = errors_of('Crate<int> c = Crate<int>()', top='interface Printable\n    string function label()\n\n'
                      'class Crate<T> implements Printable\n    T item\n\n')
    assert "Class 'Crate' implements Printable but has no function 'label' - string function label()" in found


def test_a_generic_struct_building_on_a_struct():
    assert run('Tagged<int> t = Tagged("Ada", 7)\nprint("{@1} {@2} {@3}", t.name, t.tag, nameOf(t))',
               top='struct Person\n    string name\n\nstruct Tagged<T> implements Person\n    T tag\n\n'
                   'string function nameOf(Person p) : p.name\n\n') == ['Ada 7 Ada']


# ---------------------------------------------------------------- 33.2d conditions (D.167)

CONDITIONS = ('interface Comparable\n'
              '    int function compareTo(int other)\n\n'
              'interface Printable\n'
              '    string function label()\n\n'
              'class Vehicle\n'
              '    public string name\n'
              '    constructor(string name)\n'
              '        this.name = name\n\n'
              'class Car inherits Vehicle implements Comparable, Printable\n'
              '    public int speed\n'
              '    constructor(string name, int speed)\n'
              '        super(name)\n'
              '        this.speed = speed\n'
              '    int function compareTo(int other) : speed - other\n'
              '    string function label() : "car {name}"\n\n'
              'class Aircraft\n'
              '    public string name\n'
              '    constructor(string name)\n'
              '        this.name = name\n\n'
              'T function biggest<T implements Comparable>(List<T> xs)\n'
              '    T best = xs[0]\n'
              '    for x in xs\n'
              '        if x.compareTo(best.speed) > 0\n'
              '            best = x\n'
              '    return best\n\n'
              'T function total<T extends Number>(List<T> xs)\n'
              '    T sum = xs[0]\n'
              '    int i = 1\n'
              '    while i < xs.len()\n'
              '        sum = sum + xs[i]\n'
              '        i = i + 1\n'
              '    return sum\n\n'
              'int function count<T extends int>(List<T> xs) : xs.len()\n\n'
              'string function park<T : Vehicle>(T v) : v.name\n\n'
              'string function parkToo<T extends Vehicle>(T v) : v.name\n\n'
              'string function show<T implements Comparable, Printable>(T x) : x.label()\n\n'
              'string function rank<T extends Vehicle implements Comparable>(T v) : v.name\n\n'
              'class Box<T implements Printable>\n'
              '    T item\n'
              '    constructor(T item)\n'
              '        this.item = item\n'
              '    string function shown() : item.label()\n\n'
              'struct Tagged<T extends Number, K>\n'
              '    T amount\n'
              '    K tag\n\n')


@pytest.mark.parametrize('body, lines', [
    ('List<Car> cars = [Car("a", 5), Car("b", 9), Car("c", 2)]\nprint(biggest(cars).name)', ['b']),
    ('List<double> ds = [1.5, 2.5]\nList<int> ns = [1, 2, 3]\nprint("{@1} {@2}", total(ds), total(ns))', ['4.000000 6']),
    ('List<int> ns = [1, 2]\nprint("{@1}", count(ns))', ['2']),
    ('print(park(Car("d", 1)))\nprint(park(Vehicle("v")))\nprint(parkToo(Car("e", 2)))', ['d', 'v', 'e']),
    ('Car c = Car("f", 3)\nprint(show(c))\nprint(rank(c))', ['car f', 'f']),
    ('Box<Car> b = Box(Car("g", 4))\nprint(b.shown())', ['car g']),
    ('Tagged<int, string> t = Tagged(5, "five")\nprint("{@1} {@2}", t.amount, t.tag)', ['5 five']),
])
def test_conditions_met(body, lines):
    assert run(body, top=CONDITIONS) == lines


@pytest.mark.parametrize('body, message', [
    ('List<Aircraft> a = [Aircraft("x")]\nAircraft b = biggest(a)',
     "'biggest' <T implements Comparable>: Aircraft doesn't implement Comparable"),
    ('List<string> s = ["a"]\nstring t = total(s)', "'total' <T extends Number>: string is not a number type"),
    ('List<double> d = [1.0]\nint c = count(d)', "'count' <T extends int>: double is not int - only int is accepted"),
    ('string n = park(Aircraft("x"))', "'park' <T extends Vehicle>: Aircraft is not Vehicle or a child of it"),
    ('string n = park<Aircraft>(Aircraft("x"))', "Aircraft is not Vehicle or a child of it"),
    ('string n = show(Vehicle("v"))', "Vehicle doesn't implement Comparable"),
    ('string n = rank(Vehicle("v"))', "'rank' <T extends Vehicle implements Comparable>: Vehicle doesn't implement"),
    ('Box<Aircraft> b', "'Box' <T implements Printable>: Aircraft doesn't implement Printable"),
    ('Box<Vehicle> b = Box(Vehicle("v"))', "Vehicle doesn't implement Printable"),
    ('Tagged<string, int> t = Tagged("a", 1)', "string is not a number type"),
])
def test_a_condition_not_met_is_an_error_at_the_use(body, message):
    found = errors_of(body, top=CONDITIONS)
    assert any(message in e for e in found), found


@pytest.mark.parametrize('top, message', [
    ('T function f<T extends Nothing>(T x) : x\n\n', "no class or struct 'Nothing'"),
    ('interface I\n    int function n()\n\nT function f<T extends I>(T x) : x\n\n', "write <T implements I>"),
    ('class C\n    int x\n\nT function f<T implements C>(T x) : x\n\n', "'C' is not an interface - write <T extends C>"),
    ('T function f<T implements Nothing>(T x) : x\n\n', "'Nothing' is not an interface"),
])
def test_a_condition_names_something_that_exists(top, message):
    found = errors_of('print("x")', top=top)
    assert any(message in e for e in found), found


# ---------------------------------------------------------------- 33.2e int... numbers, T... (one type)

VARIADIC = ('class Vehicle\n'
            '    public string name\n'
            '    constructor(string name)\n'
            '        this.name = name\n\n'
            'class Car inherits Vehicle\n'
            '    constructor(string name)\n'
            '        super(name)\n\n'
            'class Bus inherits Vehicle\n'
            '    constructor(string name)\n'
            '        super(name)\n\n'
            'class Counter\n'
            '    public int total = 0\n'
            '    void function addAll(int... ns)\n'
            '        for n in ns\n'
            '            total = total + n\n\n'
            'int function sum(int... numbers)\n'
            '    int total = 0\n'
            '    for n in numbers\n'
            '        total = total + n\n'
            '    return total\n\n'
            'string function joinAll(string sep, string... parts)\n'
            '    string text = ""\n'
            '    for p in parts\n'
            '        if text != ""\n'
            '            text = text + sep\n'
            '        text = text + p\n'
            '    return text\n\n'
            'T function firstOf(T... items) : items[0]\n\n'
            'int function howMany(T... items) : items.len()\n\n'
            'string function parkAll<T extends Vehicle>(T... vs)\n'
            '    string names = ""\n'
            '    for v in vs\n'
            '        names = names + v.name + " "\n'
            '    return names.trim()\n\n')


@pytest.mark.parametrize('body, lines', [
    ('print("{@1} {@2}", sum(1, 2, 3), sum())', ['6 0']),                     # values, none
    ('int[3] a = [4, 5, 6]\nList<int> xs = [7, 8]\nprint("{@1} {@2}", sum(a), sum(xs))', ['15 15']),   # array, List
    ('print(joinAll(", ", "x", "y", "z"))\nprint("[{@1}]", joinAll("-"))', ['x, y, z', '[]']),        # after a fixed one
    ('List<string> names = ["Ada", "Bo"]\nprint("{@1} {@2}", firstOf(names), firstOf("p", "q"))', ['Ada p']),
    ('int[3] a = [1, 2, 3]\nprint("{@1} {@2}", firstOf(9, 8), howMany(a))', ['9 3']),
    ('Car c = Car("mini")\nBus b = Bus("big")\nprint(parkAll(c, b))\nprint(c.name)', ['mini big', 'mini']),  # lent
    ('print(parkAll(Car("c1"), Car("c2")))', ['c1 c2']),
    ('Counter k = Counter()\nk.addAll(1, 2)\nk.addAll()\nprint("{@1}", k.total)', ['3']),            # a method
    ('string s = firstOf<string>("only")\nprint(s)', ['only']),
])
def test_variadic(body, lines):
    assert run(body, top=VARIADIC) == lines


@pytest.mark.parametrize('top, body, message', [
    ('', 'print(firstOf(1, "a"))', "a pack: the result is T"),     # a pack - but T as the result
    ('', 'int n = howMany()', "T can't be worked out from the arguments"),
    ('', 'int n = sum("a", "b")', "string"),
    ('int function bad(int... ns, int last) : last\n\n', 'print("x")', "must be the last parameter"),
])
def test_variadic_mistakes(top, body, message):
    found = errors_of(body, top=VARIADIC + top)
    assert any(message in e for e in found), found


# ---------------------------------------------------------------- 33.2e2 a pack: values of any type each

PACKS = ('class Car\n'
         '    public string name\n'
         '    constructor(string name)\n'
         '        this.name = name\n\n'
         'struct Point\n'
         '    int x\n'
         '    int y\n\n'
         'void function show(T... items)\n'
         '    print("{@1} values", items.len())\n'
         '    for x in items\n'
         '        print("{@1}", x)\n\n'
         'string function describe(string title, T... items)\n'
         '    string text = title\n'
         '    foreach (T x in items)\n'
         '        T copy = x\n'
         '        text = text + " [" + typeOf(copy) + "]"\n'
         '    return text\n\n'
         'string function tagged<K, T>(K tag, T... items)\n'
         '    return format("{@1}:{@2}:{@3}", tag, len(items), items[1])\n\n')


@pytest.mark.parametrize('body, lines', [
    ('show(1, "two", 3.5)', ['3 values', '1', 'two', '3.500000']),
    ('show(true, \'c\')\nshow(false, \'d\')', ['2 values', 'true', 'c', '2 values', 'false', 'd']),   # one copy
    ('Car c = Car("mini")\nprint(describe("t:", 1, "a", c, Point(1, 2)))\nprint(c.name)',
     ['t: [int] [string] [Car] [Point]', 'mini']),                               # an object lent, still usable
    ('print(tagged(7, "x", 2.5))', ['7:2:2.500000']),                              # with another type parameter
    ('show(1, 2)', ['2 values', '1', '2']),                                        # one type - a List as before
])
def test_packs(body, lines):
    assert run(body, top=PACKS) == lines


def test_one_copy_per_combination():
    program = parse(PACKS + 'void function main()\n    show(1, "a")\n    show(2, "b")\n    show("c", 3)\n')
    SemanticAnalyzer().analyze(program)
    names = sorted(d.name for d in program.declarations if getattr(d, 'generic_of', None) == 'show')
    assert names == ['show__int__string', 'show__string__int']


@pytest.mark.parametrize('top, body, message', [
    ('T function firstOf(T... items) : items[0]\n\n', 'print(firstOf(1, "a"))', "the result is T"),
    ('int function f(T... items)\n    int i = 0\n    return items[i]\n\n', 'int n = f(1, "a")',
     "takes a number written in the code"),
    ('void function f(T... items)\n    print(items)\n\n', 'f(1, "a")', "not passed or kept whole"),
    ('void function f(T... items)\n    List<T> all = items\n\n', 'f(1, "a")', "T is used outside 'for x in items'"),
    ('void function f(T a, T... items)\n    print("x")\n\n', 'f(1, 2, "b")', "T is int already, from an earlier"),
    ('void function f(T... items)\n    for x in items\n        break\n\n', 'f(1, "a")', "break / continue"),
    ('void function f(T... items)\n    foreach (int x in items)\n        print("{@1}", x)\n\n', 'f(1, "a")',
     "names its item T, or no type"),
    ('void function f<T extends int>(T... items)\n    print("x")\n\n', 'f(1, "a")', "each must meet <T extends int>"),
])
def test_pack_mistakes(top, body, message):
    found = errors_of(body, top=top)
    assert any(message in e for e in found), found


def test_condition_parsing():
    program = parse('T1 function f<T implements Comparable, Printable, T1 : Vehicle, K>(T a, T1 b, K c) : b\n\n'
                    'void function main()\n    print("x")\n')
    f = program.declarations[0]
    assert f.type_params == ['T', 'T1', 'K']
    assert f.type_conditions['T'] == (None, ['Comparable', 'Printable'])
    assert f.type_conditions['T1'][0].name == 'Vehicle'
    assert 'K' not in f.type_conditions


# ---------- 33.4 features tested together (the ChatGPT review; files/Ownership.md truth table 3b) ----------

TOGETHER = (
    'interface Printable\n'
    '    string function label()\n'
    '\n'
    'class Car implements Printable\n'
    '    public string name\n'
    '    public int seats\n'
    '    constructor(string name, int seats)\n'
    '        this.name = name\n'
    '        this.seats = seats\n'
    '    string function label() : "car {name}"\n'
    '\n'
    'struct Spot\n'
    '    int row\n'
    '    Car car\n'
    '\n'
    'class Garage<T implements Printable>\n'
    '    List<T> items\n'
    '    constructor()\n'
    '        items = []\n'
    '    void function park(T item)\n'
    '        items.add(item)\n'
    '    int function count() : items.len()\n'
    '    T function at(int i) : items[i]\n'
    '    string function labels()\n'
    '        string all = ""\n'
    '        for x in items\n'
    '            all = all + x.label() + ";"\n'
    '        return all\n'
    '\n'
    'T function firstOf<T>(List<T> xs) : xs[0]\n'
    '\n'
    'T function total<T extends Number>(List<T> xs)\n'
    '    T sum = xs[0]\n'
    '    for i in 1...xs.len() - 1\n'
    '        sum = sum + xs[i]\n'
    '    return sum\n'
    '\n'
    'T function keep<T>(T item)\n'
    '    T x = item\n'
    '    return x\n'
    '\n'
    'void function show(T... items)\n'
    '    for x in items\n'
    '        print("{@1}", x)\n'
    '\n\n')

TOGETHER_MAIN = '\n'.join([
    'Car a = Car("mini", 4)',
    'Car b = Car("van", 8)',
    'Garage<Car> g = Garage<Car>()',
    'g.park(a)',
    'g.park(b)',
    'print("{@1} {@2}", g.count(), g.labels())',
    'print(g.at(1).name)',
    'List<Car> cars = [Car("cab", 5), Car("bus", 40)]',
    'Car c = firstOf(cars)',
    'print("{@1} {@2}", c.name, cars.len())',
    'List<int> seats = []',
    'for car in cars',
    '    seats.add(car.seats)',
    'print("{@1}", total(seats))',
    'Spot s = Spot(1, Car("taxi", 4))',
    'Spot t = byVal s',
    't.row = 2',
    'print("{@1} {@2} {@3}", s.row, t.row, t.car.name)',
    'show(1, "two", s.car.name)',
    'for i in 0...10 step 5',
    '    print("{@1}", i)',
    'Car k = keep(Car("kept", 2))',
    'print(k.label())',
])


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_features_together(ownership):
    """A generic class holding objects in a List, under a condition (implements); a generic function over a
    List of objects and one over numbers (extends Number); a struct holding an object, copied with byVal; a
    pack; a range with a step; a generic keeping its parameter - strict and relaxed, under the leak check."""
    assert run(TOGETHER_MAIN, top=TOGETHER, memory_config=MemoryConfig(assignment=ownership)) == [
        '2 car mini;car van;', 'van', 'cab 2', '45', '1 2 taxi', '1', 'two', 'taxi', '0', '5', '10', 'car kept']


KEEPS = 'class Car\n    public string name\n    constructor(string name)\n        this.name = name\n\n'


@pytest.mark.parametrize('function', [
    'Car function keep(Car item)\n    Car x = item\n    return x\n\n',
    'T function keep<T>(T item)\n    T x = item\n    return x\n\n',
])
def test_a_generic_keeping_its_parameter_takes_it_as_a_plain_function_does(function):
    # Ownership.md 3b: `T x = item`, T a class - the rule of the real type (D.100)
    found = errors_of('Car c = Car("a")\nCar k = keep(c)\nprint(k.name)\nprint(c.name)', top=KEEPS + function)
    assert len(found) == 1 and "'c' was moved to 'keep" in found[0], found


def test_a_generic_returns_an_object_from_a_list_shared_and_a_number_copied():
    assert run('List<Car> cars = [Car("cab"), Car("bus")]\nCar c = firstOf(cars)\nc.name = "taxi"\n'
               'print("{@1} {@2} {@3}", c.name, cars[0].name, cars.len())\n'
               'List<int> ns = [4, 5]\nint n = firstOf(ns)\nn = 9\nprint("{@1} {@2}", n, ns[0])',
               top=KEEPS + 'T function firstOf<T>(List<T> xs) : xs[0]\n\n') == ['taxi taxi 2', '9 4']


@pytest.mark.parametrize('ownership, moved', [('move', True), ('share', False)])
def test_a_generic_struct_holding_an_object_copied(ownership, moved):
    # D.097: under strict it moves as a whole (byVal copies it); under relaxed the copy shares its object
    top = KEEPS + 'struct Slot<T>\n    int n\n    T item\n\n'
    found = errors_of('Slot<Car> s = Slot(1, Car("a"))\nSlot<Car> t = s\nprint(s.item.name)', top=top,
                      memory_config=MemoryConfig(assignment=ownership))
    assert any("'s' was moved to 't'" in e for e in found) == moved, found


# ---------- 33.5 a generic's types from where it is stored (Q.042 -> D.171) ----------

LEFT = (KEEPS + 'class Vehicle\n    public string name\n    constructor(string name)\n        this.name = name\n\n'
        'class Van inherits Vehicle\n    constructor(string name)\n        super(name)\n\n'
        'class Garage<T>\n    List<T> items\n    void function park(T item)\n        items.add(item)\n'
        '    int function count() : items.len()\n\n'
        'class Box<T>\n    T item\n    constructor(T item)\n        this.item = item\n    T function take() : item\n\n'
        'class Shop\n    public Garage<Car> spare\n\n'
        'Garage<Car> function newGarage() : Garage()\n\n'
        'int function sizeOf(Garage<Car> g) : g.count()\n\n')


@pytest.mark.parametrize('ownership', ['move', 'share'])
def test_the_types_come_from_where_it_is_stored(ownership):
    # a variable, set again, a result, a parameter, a field; a List<T> field starts empty - no constructor needed
    assert run('Garage<Car> g = Garage()\ng.park(Car("a"))\ng = Garage()\ng.park(Car("b"))\ng.park(Car("c"))\n'
               'Garage<Car> h = newGarage()\nShop s = Shop()\ns.spare = Garage()\n'
               'print("{@1} {@2} {@3} {@4}", g.count(), h.count(), sizeOf(Garage()), s.spare.count())',
               top=LEFT, memory_config=MemoryConfig(assignment=ownership)) == ['2 0 0 0']


def test_the_left_wins_and_the_arguments_are_checked_against_it():
    assert run('Box<Vehicle> v = Box(Van("mini"))\nBox<int> b = Box(5)\nprint("{@1} {@2}", v.take().name, b.take())',
               top=LEFT) == ['mini 5']
    assert errors_of('Box<Car> b = Box("hat")', top=LEFT) == ["Argument 1 to 'Box<Car>.new': expected Car, got string"]


@pytest.mark.parametrize('body, message', [
    ('Garage<Car> g = Box(Car("x"))', "'Box(...)' is given where Garage<Car> is expected"),
    ('var g = Garage()', "T can't be worked out from the arguments - write the types: Garage<int>(...), or on the "
                         "left: Garage<...> x = Garage(...) (D.166, D.171)"),
])
def test_types_from_the_left_mistakes(body, message):
    found = errors_of(body, top=LEFT)
    assert message in found[0], found
    assert not any('Cannot assign' in e for e in found), found
