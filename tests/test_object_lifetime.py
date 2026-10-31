"""Tests for Task 32.10c - every case in Object_Lifetime.md's catalogue.

Each program is built with -DFUSION_TRACE_OBJECTS, so every object freed shows `[freed A]` in
the output where it happens - a test checks the object went at the right moment, not only
that it went - and with the leak check (exit 5: an object never freed).

The catalogue's numbers: U - the count goes up, D - leaving a scope, R - replacing what a holder
holds, C - collections letting go, T - temporaries, O - objects holding objects. Not here:
U6 / U7 (copies of objects, a struct holding one - need clone() and [structs] classes), U10
(statics), F (free / deallocate), T4 (a match works on enums, numbers and text, not objects),
O3 / O4 - cycles - are at the end (Task 32.10d): a warning where a class can hold itself, and
the leak check stopping a program that keeps a circle.
"""

import os
import subprocess

import pytest

from src.codegen import CCodeGenerator
from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from tests.test_structs import main

CLASSES = 'class A\n    public int n\n\nclass B\n    public int n\n\n'


def analyzed(source: str):
    program = Parser(Lexer(source, 'test.fusion').tokenize()).parse_program()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    assert not analyzer.get_errors(), analyzer.get_errors()
    return analyzer, program


def built(source: str, tmp_path):
    """The program's run: (exit code, output lines, stderr)."""
    _, program = analyzed(source)
    c_file, exe = os.path.join(tmp_path, 'out.c'), os.path.join(tmp_path, 'out.exe')
    with open(c_file, 'w', encoding='utf-8') as f:
        f.write(CCodeGenerator().generate(program))
    build = subprocess.run(['gcc', '-Wall', '-DFUSION_LEAK_CHECK', '-DFUSION_TRACE_OBJECTS',
                            c_file, '-o', exe], capture_output=True, text=True)
    assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr
    result = subprocess.run([exe], capture_output=True, text=True)
    return result.returncode, result.stdout.strip().splitlines(), result.stderr


def traced(source: str, tmp_path) -> list:
    code, lines, err = built(source, tmp_path)
    assert code == 0, err                                 # 5: an object never freed
    return lines


def test_u1_u2_r2_held_until_the_last_holder_lets_go(tmp_path):
    assert traced(CLASSES + main('A a = A()\n'          # U1
                                 'A d = a\n'            # U2
                                 'a = null\n'           # R2: d still holds it
                                 'print("still held")\n'
                                 'd = null\n'
                                 'print("end")'), tmp_path) == \
        ['still held', '[freed A]', 'end']


def test_d1_d2_a_block_and_a_function_end(tmp_path):
    assert traced(CLASSES + 'void function scopes()\n'
                            '    A one = A()\n'
                            '    if true\n'
                            '        B inner = B()\n'
                            '        print("in block")\n'
                            '    print("after block")\n\n'
                  + main('scopes()\nprint("end")'), tmp_path) == \
        ['in block', '[freed B]', 'after block', '[freed A]', 'end']


def test_d3_u5_return_frees_the_rest_and_moves_the_result(tmp_path):
    assert traced(CLASSES + 'int function early()\n'
                            '    A first = A()\n'
                            '    B second = B()\n'
                            '    if true\n'
                            '        return 1\n'
                            '    return 2\n\n'
                            'A function returnsLocal()\n'
                            '    A mine = A()\n'
                            '    B other = B()\n'
                            '    return mine\n\n'
                  + main('int r = early()\n'
                         'A got = returnsLocal()\n'
                         'print("got it {r}")\n'
                         'got = null\n'
                         'print("end")'), tmp_path) == \
        ['[freed B]', '[freed A]', '[freed B]', 'got it 1', '[freed A]', 'end']


def test_d4_d8_break_continue_and_each_pass(tmp_path):
    assert traced(CLASSES + main('for i in range(0, 3)\n'
                                 '    A each = A()\n'
                                 '    if i == 1\n'
                                 '        continue\n'
                                 '    if i == 2\n'
                                 '        break\n'
                                 '    print("pass {i}")\n'
                                 'print("end")'), tmp_path) == \
        ['pass 0', '[freed A]', '[freed A]', '[freed A]', 'end']


def test_d5_break_in_a_match(tmp_path):
    assert traced(CLASSES + main('match 2\n'
                                 '    case 2\n'
                                 '        A inMatch = A()\n'
                                 '        break\n'
                                 '    else: print("other")\n'
                                 'print("end")'), tmp_path) == ['[freed A]', 'end']


def test_d6_d7_errors_and_throw_leave_their_scopes(tmp_path):
    assert traced(CLASSES + 'A, Error function failing(bool bad)\n'
                            '    B local = B()\n'
                            '    if bad\n'
                            '        return Error("bad")\n'
                            '    return A()\n\n'
                            'void function throws()\n'
                            '    B local = B()\n'
                            '    throw Error("thrown")\n\n'
                  + main('A ok, Error err = failing(true)\n'
                         'print("failed: {err.message}")\n'
                         'try\n'
                         '    A inTry = A()\n'
                         '    throws()\n'
                         'catch e\n'
                         '    print("caught {e.message}")\n'
                         'finally\n'
                         '    print("finally")\n'
                         'print("end")'), tmp_path) == \
        ['[freed B]', 'failed: bad', '[freed B]', '[freed A]', 'caught thrown', 'finally', 'end']


def test_d9_module_variables_go_last(tmp_path):
    assert traced(CLASSES + 'A shared\n\n'
                            'void function store(A x)\n'
                            '    shared = x\n\n'      # U8: borrowed; +1 only where stored
                  + main('store(A())\n'
                         'B local = B()\n'
                         'print("end")'), tmp_path) == ['end', '[freed B]', '[freed A]']


def test_r1_r3_r5_replacing_and_swapping(tmp_path):
    assert traced(CLASSES + 'class Holder\n    public A a\n\n'
                  + main('A c = A()\n'
                         'c = c\n'                        # R1: safe - nothing freed
                         'print("same")\n'
                         'c = A()\n'                      # R1
                         'print("replaced")\n'
                         'Holder h = Holder()\n'
                         'h.a = A()\n'
                         'h.a = A()\n'                    # R3
                         'print("field replaced")\n'
                         'A x = A()\n'
                         'A y = A()\n'
                         'A t = x\n'
                         'x = y\n'
                         'y = t\n'                        # R5: counts end where they started
                         't = null\n'
                         'print("swapped")\n'
                         'x = null\n'
                         'y = null\n'
                         'print("end")'), tmp_path) == \
        ['same', '[freed A]', 'replaced', '[freed A]', 'field replaced', 'swapped',
         '[freed A]', '[freed A]', 'end', '[freed Holder]', '[freed A]', '[freed A]']


def test_u3_u4_u9_c1_c2_r4_collections_of_objects(tmp_path):
    assert traced(CLASSES + 'class Holder\n'
                            '    public List<A> items\n'
                            '    public Map<string, A> named\n'
                            '    Holder function keep() : this\n\n'
                  + main('Holder h = Holder()\n'
                         'h.items.add(A())\n'              # U4
                         'h.items.add(A())\n'
                         'h.items[0] = A()\n'              # R4
                         'print("element replaced")\n'
                         'h.items.removeAt(0)\n'           # C1
                         'print("removed")\n'
                         'h.items.clear()\n'               # C2
                         'print("cleared")\n'
                         'h.named["x"] = A()\n'
                         'h.named["x"] = A()\n'            # R4
                         'print("value replaced")\n'
                         'h.named.remove("x")\n'           # C1
                         'print("map removed")\n'
                         'Holder same = h.keep()\n'        # U9: this returned and stored
                         'h = null\n'
                         'print("still held")\n'
                         'same = null\n'
                         'print("end")'), tmp_path) == \
        ['[freed A]', 'element replaced', '[freed A]', 'removed', '[freed A]', 'cleared',
         '[freed A]', 'value replaced', '[freed A]', 'map removed', 'still held',
         '[freed Holder]', 'end']


def test_c3_c4_o1_a_collection_freed_and_parts_shared(tmp_path):
    assert traced(CLASSES + 'class Box\n    public List<A> items\n\n'
                            'bool function all(A a) : true\n\n'
                  + main('List<A> xs = [A(), A()]\n'
                         'List<A> part = xs.slice(0, 1)\n'   # C4: shares the first
                         'List<A> each = xs.filter(all)\n'   # C4: shares both
                         'xs = List<A>()\n'
                         'each = List<A>()\n'                # C3: the second's last holder
                         'print("lists replaced")\n'
                         'part = List<A>()\n'
                         'print("part replaced")\n'
                         'Box b = Box()\n'
                         'b.items.add(A())\n'
                         'b = null\n'                        # O1: the box lets go of its items
                         'print("end")'), tmp_path) == \
        ['[freed A]', 'lists replaced', '[freed A]', 'part replaced', '[freed Box]',
         '[freed A]', 'end']


def test_t1_t2_t3_temporaries(tmp_path):
    assert traced(CLASSES + 'A function makeA() : A()\n\n'
                            'A function passBack(A x) : x\n\n'
                  + main('A()\n'                              # T1
                         'print("statement")\n'
                         'int n = makeA().n\n'                # T2
                         'print("read {n}")\n'
                         'passBack(A())\n'
                         'print("passed back")\n'
                         'bool pick = true\n'
                         'A chosen = pick ? A() : makeA()\n'  # T3: only the chosen one made
                         'print("chosen")\n'
                         'for a in [A(), A()]\n'              # made once, freed after the loop
                         '    print("looping")\n'
                         'print("end")'), tmp_path) == \
        ['[freed A]', 'statement', '[freed A]', 'read 0', '[freed A]', 'passed back',
         'chosen', 'looping', 'looping', '[freed A]', '[freed A]', 'end', '[freed A]']


def test_arrays_of_objects(tmp_path):
    assert traced(CLASSES + main('A[2] arr\n'
                                 'arr[0] = A()\n'
                                 'arr[0] = A()\n'
                                 'print("replaced")'), tmp_path) == \
        ['[freed A]', 'replaced', '[freed A]']


CIRCLE = ('class Node\n    public int n\n    public Node next\n\n'
          'class A\n    public B friend\n\n'
          'class B\n    public List<A> friends\n\n'
          'class Plain\n    public A one\n\n')


def test_o3_o4_a_warning_where_a_class_can_hold_itself():
    warnings = [str(w) for w in analyzed(CIRCLE + main('print("x")'))[0].get_warnings()]
    assert any("Class 'Node' can hold itself (Node -> Node)" in w for w in warnings)
    assert any("Class 'A' can hold objects that hold it in turn (A -> B -> A)" in w
               for w in warnings)
    assert not any("'B'" in w or "'Plain'" in w for w in warnings)   # one warning per circle
    assert len(warnings) == 2


def test_o3_a_circle_kept_is_reported_by_the_leak_check(tmp_path):
    code, lines, err = built(CIRCLE + main('A a = A()\n'
                                           'B b = B()\n'
                                           'a.friend = b\n'
                                           'b.friends.add(a)\n'
                                           'print("made a circle")'), tmp_path)
    assert (code, lines) == (5, ['made a circle'])
    assert "2 object(s) were never freed" in err


@pytest.mark.parametrize('body, freed', [
    # O3: break the circle before letting go - both are freed
    ('A a = A()\nB b = B()\na.friend = b\nb.friends.add(a)\na.friend = null\nprint("broken")',
     ['broken', '[freed B]', '[freed A]']),
    # O4: an object holding itself
    ('Node n = Node()\nn.next = n\nn.next = null\nprint("broken")', ['broken', '[freed Node]']),
])
def test_a_circle_broken_is_freed(body, freed, tmp_path):
    assert traced(CIRCLE + main(body), tmp_path) == freed


def generated(source: str) -> str:
    return CCodeGenerator().generate(analyzed(source)[1])


def test_returning_a_local_moves_it_without_counting():
    # 32.10e: a local returned is handed over as it is - no retain / copy, no release
    code = generated(CLASSES + 'A function makeOne()\n'
                               '    A mine = A()\n'
                               '    return mine\n\n'
                               'string function greet(string name)\n'
                               '    string s = "Hi " + name\n'
                               '    return s\n\n'
                     + main('A a = makeOne()\nprint(greet("Ann"))'))
    body = code[code.index('fu_A* fu_makeOne(void) {'):]
    body = body[:body.index('\n}')]
    assert 'return mine;' in body and 'fusion_retain_' not in body
    constructor = code[code.index('fu_A* fu_A__new(void) {'):]
    assert constructor[:constructor.index('\n}')].count('fusion_retain_') == 0
    greet = code[code.index('fusion_string fu_greet(fusion_string name) {'):]
    assert 'return s;' in greet[:greet.index('\n}')]


def test_moves_keep_every_moment_the_same(tmp_path):
    # the same frees as before 32.10e - a returned local, and one leaving through a finally
    # (not moved: the finally could still change it)
    assert traced(CLASSES + 'A function makeOne()\n'
                            '    A mine = A()\n'
                            '    B other = B()\n'
                            '    return mine\n\n'
                            'A function guarded()\n'
                            '    A kept = A()\n'
                            '    try\n'
                            '        return kept\n'
                            '    finally\n'
                            '        print("finally")\n\n'
                  + main('A a = makeOne()\n'
                         'print("made")\n'
                         'A g = guarded()\n'
                         'a = null\n'
                         'g = null\n'
                         'print("end")'), tmp_path) == \
        ['[freed B]', 'made', 'finally', '[freed A]', '[freed A]', 'end']
