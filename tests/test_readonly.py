"""Tests for Task 32.2e - readonly parameters (Object_Lifetime.md section 3), and set-up
blocks that may still change the const / let they set up (user, 2026-10-30).

A readonly parameter is read, never changed: not assigned, not through a field or element,
not by a List / Map method or a method that changes its object, not passed to a function
that changes it (found by following the calls), not kept (a field, a List, returned). A
variable that shares it (`Account b = a`) is readonly too; `byVal` makes a copy that may
change. With and without null checks (Rule 4b). Each test is a row of the table.
"""

import pytest

from tests.test_object_lifetime import traced
from tests.test_structs import errors_of, main

ACCOUNT = ('struct Point\n'
           '    int x\n'
           '    int y\n\n'
           'class Account\n'
           '    public int balance\n'
           '    public List<int> moves = List<int>()\n'
           '    void function deposit(int amount)\n'
           '        balance = balance + amount\n'
           '    void function twice(int amount)\n'
           '        deposit(amount)\n'                     # changes it through another method
           '        deposit(amount)\n'
           '    int function read() : balance\n\n'
           'List<Account> kept = List<Account>()\n\n'
           'void function update(Account a)\n'
           '    a.balance = 1\n\n'
           'void function relay(Account a)\n'
           '    update(a)\n\n'                             # changes it two calls down
           'void function look(Account a)\n'
           '    print(format("{@1}", a.balance))\n\n')


def readonly_body(body: str) -> str:
    return (ACCOUNT + 'Account function show(readonly Account a, readonly int n, readonly Point p, '
            'readonly List<int> xs)\n'
            + ''.join(f'    {line}\n' for line in body.split('\n'))
            + '    return Account()\n\n' + main('Account x = show(Account(), 1, Point(1, 2), List<int>())'))


def test_reading_and_passing_to_a_reader_runs(tmp_path):
    source = (ACCOUNT + 'void function show(readonly Account a, readonly List<int> xs)\n'
              '    print(format("{@1} {@2} {@3}", a.balance, a.read(), xs.length()))\n'
              '    look(a)\n'
              '    Account same = a\n'
              '    print(format("{@1}", same.read()))\n'
              '    List<int> mine = byVal xs\n'
              '    mine.add(9)\n'                            # a copy may change
              '    print(format("{@1} {@2}", xs.length(), mine.length()))\n\n'
              + main('Account acc = Account()\n'
                     'acc.deposit(7)\n'
                     'List<int> nums = List<int>()\n'
                     'nums.add(1)\n'
                     'show(acc, nums)'))
    assert traced(source, tmp_path)[:4] == ['7 7 1', '7', '7', '1 2']


@pytest.mark.parametrize('line, message', [
    ('a.balance = 0', "'a' is readonly - show may read it but not change it"),
    ('a = Account()', "'a' is readonly - show may read it but not change it"),
    ('a.moves.add(1)', "'a' is readonly - show may read it but not change it"),
    ('a.moves[0] = 1', "'a' is readonly - show may read it but not change it"),
    ('a.deposit(5)', "'a' is readonly - show calls deposit, which changes a"),
    ('a.twice(5)', "'a' is readonly - show calls twice, which changes a"),
    ('update(a)', "'a' is readonly - show passes it to update, which changes it"),
    ('relay(a)', "'a' is readonly - show passes it to relay, which changes it"),
    ('Account b = a\nb.balance = 2', "'a' is readonly - show may read it but not change it"),
    ('kept.add(a)', "'a' is readonly - show can't keep it"),
    ('return a', "'a' is readonly - show can't keep it"),
    ('n = 2', "'n' is readonly - show may read it but not change it"),
    ('p.x = 1', "'p' is readonly - show may read it but not change it"),
    ('xs.add(3)', "'xs' is readonly - show may read it but not change it"),
    ('xs[0] = 1', "'xs' is readonly - show may read it but not change it"),
])
def test_every_change_is_an_error(line, message):
    assert message in errors_of(readonly_body(line))


def test_copy_hint_for_a_list_and_a_function_value():
    errors = errors_of(ACCOUNT + 'void function grow(List<int> xs)\n'
                       '    xs.add(1)\n\n'
                       'void function show(readonly List<int> xs, (List<int>) -> void f)\n'
                       '    grow(xs)\n'
                       '    f(xs)\n\n' + main('print("x")'))
    assert "show passes it to grow, which changes it (use a copy: byVal xs)" in errors
    assert "'xs' is readonly - show passes it to a function value that may change it" in errors


def test_null_without_and_with_a_check(tmp_path):
    assert traced(ACCOUNT + 'void function show(readonly Account a)\n'
                            '    if a is not null\n'
                            '        print(format("{@1}", a.balance))\n'
                            '    else\n'
                            '        print("-1")\n'
                            '    try\n'
                            '        print(format("{@1}", a.balance))\n'
                            '    catch err\n'
                            '        print("caught: {err.message}")\n\n'
                  + main('show(null)'), tmp_path) == \
        ['-1', "caught: used '.' on a null Account"]


def test_set_up_block_may_change_its_const_and_let(tmp_path):
    assert traced('struct Point\n    int x\n    int y\n\n'
                  + main('const Point p = Point(1, 2) {\n'
                         '    p.x = 5\n'
                         '}\n'
                         'const List<int> nums = List<int>() {\n'
                         '    nums.add(1)\n'
                         '}\n'
                         'let q = Point(3, 4)\n'
                         '    q.y = 7\n'
                         'print(format("{@1} {@2} {@3}", p.x, q.y, nums.length()))'),
                  tmp_path) == ['5 7 1']


def test_after_its_set_up_block_a_const_is_fixed():
    assert "Cannot assign to field 'x' of constant 'p'" in errors_of(
        'struct Point\n    int x\n    int y\n\n'
        + main('const Point p = Point(1, 2) {\n    p.x = 5\n}\np.x = 6'))
