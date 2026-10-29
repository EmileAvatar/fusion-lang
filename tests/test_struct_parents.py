"""Tests for Task 32.8 - structs building on structs.

`struct Employee implements Person` (or extends / includes): Person's fields come first, then
Employee's own. An Employee goes where a Person is expected - the function gets a copy of the
Person part only. Person's methods work on an Employee. A field both have is kept twice, with
a warning, and is read as e.Person.tel / e.Employee.tel. "{e}" prints every field.

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
    assert lines == ['Hi Jeffrey, 42', 'Jeffrey E7 012 083', 'Jeffrey, 083, 42, E7, 012']


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
    assert lines == ['Jo, 1, 99', '20', 'Ann, 082, 99', 'Jo, 1, 20', 'Jo', 'Bo', 'Cy']


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
    assert lines == ['Hi Sue, 50', 'Hi Bo, 40', 'Sue, 1, 99', 'Sue, 1, 50, M1, 2, 7',
                     'Al, 5, 30, E9, 099 / dog, 4, Rex']


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
