"""Tests for Task 48.3 - at the call: `byVal`, `byRef`, `readonly` (files/Ownership.md section 4,
truth tables 1 and 4; D13-D20).

    show(readonly acc)        // fine: show only reads
    log(readonly acc)         // error here: log changes a (line 9) - and at that line too
    log(byVal acc)            // fine: log changes a copy
    log(acc)                  // fine: log borrows it, changes it, hands it back

`readonly` at a call is checked in every mode, like a readonly parameter (32.2e); the byRef
rules that come from moving need `[memory] assignment = "move"`.
"""

import pytest

from tests.test_end_to_end import SHARE
from tests.test_ownership_moves import CAR, errors, run
from tests.test_structs import main

ACCOUNT = ('class Account\n    public int balance = 5\n    public int logged = 0\n\n'
           'void function show(Account a)\n    print("{a.balance}")\n\n'
           'void function log(Account a)\n    a.logged = a.logged + 1\n\n')


# ---------- truth table 4: readonly at the call ----------

@pytest.mark.parametrize('options', [SHARE, None], ids=['share', 'move'])
def test_readonly_to_a_function_that_only_reads(options):
    source = ACCOUNT + main('Account acc = Account()\nshow(readonly acc)')
    assert (run(source, options) if options is not None else run(source)) == ['5']


@pytest.mark.parametrize('options', [SHARE, None], ids=['share', 'move'])
def test_readonly_to_a_function_that_changes_it_two_errors(options):
    source = ACCOUNT + main('Account acc = Account()\nlog(readonly acc)')
    found = errors(source, options) if options is not None else errors(source)
    assert found == ["log changes 'a' (line 9) - 'acc' is passed readonly; pass byVal acc for a copy",
                     "log changes 'a' here - line 13 passes 'acc' to log as readonly"]


def test_the_change_is_found_through_the_calls():
    source = ACCOUNT + 'void function audit(Account a)\n    log(a)\n\n' + \
        main('Account acc = Account()\naudit(readonly acc)')
    found = errors(source, SHARE)
    assert found[0].startswith("audit changes 'a' (line 9)"), found
    assert "log changes 'a' here - line 16 passes 'acc' to audit as readonly" in found


def test_a_method_changing_its_parameter():
    source = ACCOUNT + 'class Bank\n    void function close(Account a)\n        a.balance = 0\n\n' + \
        main('Bank b = Bank()\nAccount acc = Account()\nb.close(readonly acc)')
    assert any("close changes 'a' (line 13)" in e for e in errors(source, SHARE))


def test_a_function_keeping_it():
    source = ACCOUNT + 'List<Account> all = []\n\nvoid function enrol(Account a)\n    all.add(a)\n\n' + \
        main('Account acc = Account()\nenrol(readonly acc)')
    assert any("enrol keeps 'a'" in e for e in errors(source, SHARE))


def test_byval_and_a_plain_borrow_are_fine():
    source = ACCOUNT + main('Account acc = Account()\nlog(byVal acc)\nprint("{acc.logged}")\n'
                            'log(acc)\nprint("{acc.logged}")')
    assert run(source, SHARE) == ['0', '1']
    assert run(source) == ['0', '1']


def test_readonly_to_a_list_method_that_keeps_it():
    source = ACCOUNT + main('List<Account> all = []\nAccount acc = Account()\nall.add(readonly acc)')
    assert errors(source, SHARE) == ["add keeps what it is given - 'acc' is passed readonly; pass "
                                     "byVal acc for a copy"]


def test_readonly_on_a_value_that_is_copied_anyway():
    source = 'void function f(int n)\n    print("{n}")\n\n' + main('int x = 1\nf(readonly x)')
    assert errors(source, SHARE) == ["readonly at a call is for a value the function could change "
                                     "- a int is copied anyway"]


def test_readonly_only_at_a_call():
    source = ACCOUNT + main('Account acc = Account()\nAccount b = readonly acc')
    assert any("readonly is written at a call" in e for e in errors(source, SHARE))


def test_readonly_through_a_function_value():
    source = ACCOUNT + main('(Account) : void f = log\nAccount acc = Account()\nf(readonly acc)')
    found = errors(source, SHARE)
    assert any("A function value can't be looked into - 'acc' is passed readonly" in e
               for e in found) or found == [], found


# ---------- byRef on an object (truth table 1) ----------

def test_byref_on_an_object_is_allowed():
    source = ACCOUNT + main('Account acc = Account()\nlog(byRef acc)\nprint("{acc.logged}")')
    assert run(source, SHARE) == ['1']
    assert run(source) == ['1']


def test_byref_on_a_plain_struct_waits():
    source = 'struct P\n    int x\n\nvoid function f(P p)\n    print("{p.x}")\n\n' + \
        main('P p = P(1)\nf(byRef p)')
    assert any("byRef works on a List, a Map or an object" in e for e in errors(source, SHARE))


# ---------- with "move": byRef / readonly only lend ----------

GARAGE = 'class Garage\n    public Car car\n    void function park(Car c)\n        this.car = c\n\n'


@pytest.mark.parametrize('word', ['byRef', 'readonly'])
def test_lending_to_a_function_that_keeps_it(word):
    source = CAR + GARAGE + main(f'Garage g = Garage()\nCar a = Car("red")\ng.park({word} a)')
    assert any(f"park keeps its 'c' - '{word} a' only lends it for the call" in e
               for e in errors(source)), errors(source)


def test_byref_into_a_local_is_a_borrow():
    source = CAR + main('Car a = Car("red")\nCar b = byRef a\na = Car("blue")\nprint(b.color)')
    assert any("'a' can't change while 'b' borrows from it" in e for e in errors(source))
    fine = CAR + main('Car a = Car("red")\nCar b = byRef a\nb.color = "blue"\nprint(a.color)')
    assert run(fine) == ['blue']


def test_byref_cant_be_stored():
    source = CAR + GARAGE + main('Garage g = Garage()\nCar a = Car("red")\ng.car = byRef a')
    assert any("'byRef a' only lends it - a borrow can't be stored or returned" in e
               for e in errors(source))


# ---------- nulls (Rule 4b) ----------

def test_without_a_null_check_a_readonly_null_is_a_null_error():
    source = ACCOUNT + main('Account acc = null\ntry\n    show(readonly acc)\ncatch NullError e\n'
                            '    print("null")')
    assert run(source, SHARE) == ['null']


def test_with_a_null_check_the_readonly_call_runs_on():
    source = ACCOUNT + main('Account acc = null\nif acc is not null\n    show(readonly acc)\n'
                            'print("done")')
    assert run(source, SHARE) == ['done']


def test_a_null_error_inside_a_called_function_reaches_the_catch():
    # found with 48.3: a function using '.' on a null object didn't count as one that can
    # fail, so its caller never checked - the catch was skipped and the error dropped
    caught = ACCOUNT + main('Account acc = null\ntry\n    show(acc)\ncatch NullError e\n    print("null")')
    assert run(caught, SHARE) == ['null']
    from tests.test_end_to_end import compile_and_run
    code, out, err = compile_and_run(ACCOUNT + main('Account acc = null\nshow(acc)\nprint("after")'))
    assert code != 0 and "used '.' on a null Account" in err and 'after' not in out
