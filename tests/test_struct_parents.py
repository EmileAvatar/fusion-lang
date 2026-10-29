"""Tests for Task 32.8 - structs building on structs.

`struct Employee implements Person` (or extends / includes): Person's fields come first, then
Employee's own. An Employee goes where a Person is expected - the function gets a copy of the
Person part only. Person's methods work on an Employee. A field both have is kept twice, with
a warning, and is read as e.Person.tel / e.Employee.tel. "{e}" prints every field as
`name : value` (Task 32.13), and x.toCSV() gives a heading row and rows of values.

A struct is never null, so the with / without null check rule (4b) has nothing to test here.
"""

import pytest

from src.config import StructsConfig
from tests.test_struct_methods import analyze, errors, run
from tests.test_structs import main

ON = StructsConfig(functions=True)

PEOPLE = ('struct Person\n'
          '    string name\n'
          '    string tel\n'
          '    int age = 30\n\n'
          '    void function greet()\n'
          '        print("Hi {name}, {age}")\n\n'
          '    void function birthday()\n'
          '        age = age + 1\n\n'
          'struct Employee implements Person\n'
          '    string employeeID\n'
          '    string tel\n\n'
          '    void function show()\n'
          '        greet()\n'
          '        print("{name} {employeeID} {this.Employee.tel} {this.Person.tel}")\n\n'
          'struct Manager extends Employee\n'
          '    int reports\n\n'
          'Employee function hire(string n) : Employee(n, "082", 40, "E1", "011")\n\n'
          'void function welcome(Person p)\n'
          '    p.age = 99\n'
          '    print("{p}")\n\n')


def warnings(source: str) -> list:
    return [str(w) for w in analyze(source)[0].get_warnings()]


def test_fields_methods_and_the_parts(tmp_path):
    lines = run(PEOPLE + main('Employee e = Employee("Jeff", "082", 41, "E7", "011")\n'
                              'e.name = "Jeffrey"\n'
                              'e.Person.tel = "083"\n'
                              'e.Employee.tel = "012"\n'
                              'e.birthday()\n'
                              'e.show()\n'
                              'print("{e}")'), tmp_path)
    assert lines == ['Hi Jeffrey, 42', 'Jeffrey E7 012 083',
                     'name : "Jeffrey",Person.tel : "083",age : 42,employeeID : "E7",'
                     'Employee.tel : "012"']


def test_an_employee_goes_where_a_person_is_expected(tmp_path):
    lines = run(PEOPLE + 'Person function demote(Employee e) : e\n\n'
                + main('Employee e = Employee("Jo", "1", 20, "E2", "2")\n'
                       'welcome(e)\n'                     # a copy of the Person part
                       'print("{e.age}")\n'
                       'welcome(hire("Ann"))\n'           # a fresh one
                       'Person p = e\n'
                       'p = hire("Bo")\n'
                       'Person d = demote(e)\n'
                       'print("{d}")\n'
                       'List<Person> people = [e, p]\n'
                       'people.add(hire("Cy"))\n'
                       'for x in people\n'
                       '    print(x.name)'), tmp_path)
    assert lines == ['name : "Jo",tel : "1",age : 99', '20', 'name : "Ann",tel : "082",age : 99',
                     'name : "Jo",tel : "1",age : 20', 'Jo', 'Bo', 'Cy']


def test_a_chain_and_the_ways_to_build_one(tmp_path):
    lines = run(PEOPLE + 'struct Pet\n    string kind\n    int legs = 4\n\n'
                'struct Dog includes Pet\n    string name\n\n'
                + main('Manager m = Manager("Sue", "1", 50, "M1", "2", 7)\n'
                              'm.greet()\n'
                              'hire("Bo").greet()\n'
                              'welcome(m)\n'
                              'print(format("{@1}", m))\n'
                              'Person p = Person("Al", "5")\n'
                              'Employee e = Employee(p, "E9", "099")\n'
                       'Dog d = Dog(name = "Rex", kind = "dog")\n'
                       'print("{e} / {d}")'), tmp_path)
    assert lines == ['Hi Sue, 50', 'Hi Bo, 40', 'name : "Sue",tel : "1",age : 99',
                     'name : "Sue",Person.tel : "1",age : 50,employeeID : "M1",Employee.tel : "2",'
                     'reports : 7',
                     'name : "Al",Person.tel : "5",age : 30,employeeID : "E9",Employee.tel : "099"'
                     ' / kind : "dog",legs : 4,name : "Rex"']


def test_a_field_both_have_is_a_warning():
    found = warnings(PEOPLE + main('Employee e'))
    assert any("Struct 'Employee' has field 'tel', and so does Person - both are kept" in w
               for w in found)


@pytest.mark.parametrize('code, message', [
    ('Employee e\nstring t = e.tel',
     "Struct 'Employee' has more than one field 'tel' - write .Employee.tel or .Person.tel"),
    ('Employee e = Employee(name = "a", tel = "b")\nint x = 1',
     "Struct 'Employee' has more than one field 'tel' - give the values in order"),
    ('const Employee k = Employee("a", "b", 1, "c", "d")\nk.birthday()',
     "Method 'birthday' changes the Person - 'k' is a constant"),
    ('Person p\nEmployee e = p', "Cannot assign Person to variable of type Employee"),
])
def test_usage_errors(code, message):
    assert any(message in e for e in errors(PEOPLE + main(code)))


@pytest.mark.parametrize('source, message', [
    ('struct A implements Nope\n    int x\n', "Struct 'A' builds on 'Nope', which isn't a struct"),
    ('struct A implements B\n    int x\nstruct B implements A\n    int y\n',
     "Struct 'A' builds on itself (A -> B -> A)"),
    ('struct P\n    int x\nstruct Q implements P\n    int P\n',
     "Field 'P' of struct 'Q' can't have the name of a struct it builds on"),
    ('struct P\n    int x\n    void function f()\n        x = 1\nstruct Q implements P\n    int f\n',
     "Field 'f' of struct 'Q' has the name of a method of a struct it builds on"),
    ('struct P\n    int x\nstruct Q implements P\n    void function f(int x)\n        print("a")\n',
     "Parameter 'x' of method 'Q.f' has the name of a field"),
    ('struct P\n    Q q\nstruct Q implements P\n    int y\n', "contains itself"),
    ('struct P\n    int x\n    int[2] xs\nstruct Q implements P\n    int y\n'
     'void function main()\n    Q q\n    print("{q}")\n',
     "Can't print a whole Q: its field 'P' is a P"),
])
def test_declaration_errors(source, message):
    assert any(message in e for e in errors(source))


def test_building_on_a_struct_is_not_nesting():
    chain = ('struct A\n    int a\nstruct B implements A\n    int b\n'
             'struct C implements B\n    int c\nstruct D implements C\n    int d\n')
    assert errors(chain + main('D d'), StructsConfig(functions=True, max_nesting_depth=2)) == []


SHAPES = ('struct Point\n    int x\n    int y\n\n'
          'struct Line\n    Point a\n    Point b\n    char mark = \'q\'\n    bool on = true\n\n')


def test_a_struct_inside_a_struct_and_csv(tmp_path):
    lines = run(SHAPES + main('Line l = Line(Point(1, 2), Point(3, 4))\n'
                              'print("{l}")\n'
                              'print(l.toCSV(";"))'), tmp_path)
    assert lines == ["a : {x : 1,y : 2},b : {x : 3,y : 4},mark : 'q',on : true",
                     'Line.a.x;Line.a.y;Line.b.x;Line.b.y;Line.mark;Line.on',
                     '1;2;3;4;"q";true']


def test_csv_of_a_struct_an_array_and_a_list(tmp_path):
    lines = run(PEOPLE + main('Employee e = Employee("Jeff \\"J\\"", "082", 41, "E7", "011")\n'
                              'print(e.toCSV())\n'
                              'Employee[] staff = [e, hire("Ann")]\n'
                              'print(staff.toCSV())\n'
                              'List<Person> people = [e, Person("Bo", "9")]\n'
                              'string s = people.toCSV(\'|\')\n'
                              'print(s)'), tmp_path)
    assert lines == ['Person.name,Person.tel,Person.age,Employee.employeeID,Employee.tel',
                     '"Jeff ""J""","082",41,"E7","011"',
                     'Person.name,Person.tel,Person.age,Employee.employeeID,Employee.tel',
                     '"Jeff ""J""","082",41,"E7","011"',
                     '"Ann","082",40,"E1","011"',
                     'Person.name|Person.tel|Person.age',
                     '"Jeff ""J"""|"082"|41',
                     '"Bo"|"9"|30']


def test_a_structs_own_tocsv_comes_first(tmp_path):
    lines = run('struct P\n    int x\n    string function toCSV() : "mine"\n\n'
                + main('P p = P(1)\nprint(p.toCSV())'), tmp_path)
    assert lines == ['mine']


@pytest.mark.parametrize('code, message', [
    ('Bag b\nstring s = b.toCSV()', "Can't make CSV from a Bag: its field 'items' is a int[2]"),
    ('Point p\nstring s = p.toCSV(1)', "The delimiter of toCSV is a string or char, not int"),
    ('Point p\nstring s = p.toCSV(";", ",")', "toCSV takes one value, the delimiter"),
    ('int n = 1\nstring s = n.toCSV()', "has no method 'toCSV'"),
])
def test_csv_errors(code, message):
    source = SHAPES + 'struct Bag\n    int[2] items\n\n' + main(code)
    assert any(message in e for e in errors(source))
