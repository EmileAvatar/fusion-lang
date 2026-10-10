"""Tests for Task 18.3 - proper strings.

18.3.1: strings are values with automatic cleanup - each variable, field and array element
        owns its text, copies are independent, and every owned string is freed exactly once
        (end of block, return, break, continue, end of statement for temporaries).
        `==`/`!=` compare text, `<`/`>` compare alphabetically.

Every end-to-end test here runs under the leak check (compile_and_run builds with
-DFUSION_LEAK_CHECK): exit code 3 means a string was never freed, 4 means freed twice. In
that mode every copy really allocates, so a missing or doubled free can't hide behind the
"source text is shared" shortcut.
"""

import os
import subprocess
import tempfile

import pytest

from src.codegen.c_memory import RUNTIME_PRELUDE
from src.config import StructsConfig
from tests.test_structs import parse, analyze, errors_of, generate_c, main
from tests.test_end_to_end import compile_and_run


ECHO = 'string function echo(string s)\n    return s\n'
BOOK = 'struct Book\n    string title\n    string[2] tags\n\n'


def run_ok(source: str) -> list:
    """Compile and run under the leak check; return stdout lines."""
    exit_code, stdout, stderr = compile_and_run(source)
    assert exit_code == 0, f"exit {exit_code}: {stderr}"
    return stdout.splitlines()


# ============================================================
# The runtime and its leak check
# ============================================================

def _run_runtime_snippet(body: str) -> int:
    """Compile a C program made of the runtime plus `body` (as main's body), under the leak
    check, and return its exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        c_file = os.path.join(tmp, 'leak.c')
        exe = os.path.join(tmp, 'leak.exe')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write('#include <stdarg.h>\n#include <stdbool.h>\n#include <stdint.h>\n#include <stdio.h>\n'
                    '#include <stdlib.h>\n#include <string.h>\n' + RUNTIME_PRELUDE
                    + 'int main(void) {\n' + body + '\n    return 0;\n}\n')
        build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', c_file, '-o', exe],
                               capture_output=True, text=True)
        assert build.returncode == 0, build.stderr
        return subprocess.run([exe], capture_output=True).returncode


def test_leak_check_passes_when_everything_is_freed():
    assert _run_runtime_snippet(
        '    fusion_string s = fusion_str_copy(FUSION_STR("x"));\n    fusion_str_free(&s);') == 0


def test_leak_check_catches_a_string_never_freed():
    assert _run_runtime_snippet('    fusion_string s = fusion_str_copy(FUSION_STR("x")); (void)s;') == 3


def test_leak_check_catches_a_double_free():
    assert _run_runtime_snippet(
        '    fusion_string s = fusion_str_copy(FUSION_STR("x"));\n'
        '    fusion_string t = s;\n    fusion_str_free(&s);\n    fusion_str_free(&t);') == 4


def test_runtime_is_in_every_program():
    c_code = generate_c(main('int x = 1'))
    assert 'typedef struct { char* data; int len; int chars; int owned; } fusion_string;' in c_code


# ============================================================
# Code generation
# ============================================================

def test_string_is_a_value_type():
    c_code = generate_c(main('string s = "hi"'))
    assert 'fusion_string s = FUSION_STR("hi");' in c_code
    assert 'fusion_str_free(&s);' in c_code


def test_string_without_value_is_empty():
    assert 'fusion_string s = FUSION_STR("");' in generate_c(main('string s'))


def test_copy_on_store_from_a_variable():
    c_code = generate_c(main('string a = "x"\nstring b = a'))
    assert 'fusion_string b = fusion_str_copy(a);' in c_code


def test_fresh_result_is_moved_not_copied():
    c_code = generate_c(ECHO + main('string b = echo("x")'))
    assert 'fusion_string b = echo(FUSION_STR("x"));' in c_code


def test_assignment_frees_the_old_value():
    c_code = generate_c(main('string a = "x"\na = "y"'))
    assert 'fusion_str_set(&a, FUSION_STR("y"));' in c_code


def test_unused_fresh_result_is_freed_after_the_statement():
    c_code = generate_c(ECHO + main('echo("x")'))
    assert '(fusion_tmp_' in c_code
    assert 'fusion_str_free(&fusion_tmp_' in c_code


def test_temporaries_start_empty():
    """`a and f() == "x"` may skip the call - freeing its temporary must be harmless."""
    c_code = generate_c(ECHO + main('int n = 0\nif n > 5 and echo("x") == "x"\n    print("no")'))
    assert 'fusion_string fusion_tmp_1 = FUSION_STR("");' in c_code


def test_parameter_borrowed_unless_assigned():
    c_code = generate_c(ECHO + 'string function change(string s)\n    s = "new"\n    return s\n'
                        + main('string x = change("a")'))
    echo_body = c_code[c_code.index('fusion_string echo(fusion_string s) {'):]
    assert 's = fusion_str_copy(s);' not in echo_body[:echo_body.index('}')]
    change_body = c_code[c_code.index('fusion_string change(fusion_string s) {'):]
    assert 's = fusion_str_copy(s);' in change_body[:change_body.index('}')]


def test_struct_helpers_generated_for_string_structs_only():
    c_code = generate_c(BOOK + 'struct Point\n    int x\n\n' + main('Book b\nPoint p'))
    assert 'static inline Book fusion_copy_Book(Book v) {' in c_code
    assert 'static inline void fusion_free_Book(Book* v) {' in c_code
    assert 'fusion_copy_Point' not in c_code


def test_string_comparison_by_content():
    c_code = generate_c(main('string a = "x"\nbool e = a == "x"\nbool n = a != "y"\nbool l = a < "z"'))
    assert 'bool e = fusion_str_eq(a, FUSION_STR("x"));' in c_code
    assert 'bool n = (!fusion_str_eq(a, FUSION_STR("y")));' in c_code
    assert 'bool l = (fusion_str_cmp(a, FUSION_STR("z")) < 0);' in c_code


def test_string_ordering_against_number_rejected():
    assert "must be numeric" in errors_of(main('bool b = "a" < 5'))


def test_reusing_a_string_name_in_a_nested_block_rejected():
    source = main('string s = "a"\nif true\n    string s = "b"\n    print(s)')
    with pytest.raises(NotImplementedError, match="reuses the name of a string"):
        generate_c(source)


# ============================================================
# End to end - all under the leak check
# ============================================================

def test_values_copy_independently():
    assert run_ok(ECHO + main(
        'string a = "hello"\n'
        'string b = echo(a)\n'
        'b = "changed"\n'
        'print("{@1} {@2}", a, b)\n'
        'b = a\n'
        'b = b\n'
        'print("{b}")\n'
    )) == ["hello changed", "hello"]


def test_assigning_a_parameter_never_touches_the_caller():
    assert run_ok('string function change(string s)\n    s = "new"\n    return s\n' + main(
        'string a = "old"\n'
        'string b = change(a)\n'
        'print("{@1} {@2}", a, b)\n'
    )) == ["old new"]


def test_structs_and_arrays_of_strings():
    assert run_ok(BOOK + 'struct Shelf\n    Book first\n    Book[2] more\n\n'
                  'Book function makeBook(string t)\n'
                  '    Book b = Book(t, ["x", "y"])\n'
                  '    return b\n'
                  + main(
                      'Book k = makeBook("Dune")\n'
                      'Book k2 = k\n'
                      'k2.title = "Copy"\n'
                      'k2.tags[0] = "changed"\n'
                      'print("{@1} {@2} {@3} {@4}", k.title, k.tags[0], k2.title, k2.tags[0])\n'
                      'Shelf s\n'
                      's.first = k\n'
                      's.more[1] = k2\n'
                      'Shelf s2 = s\n'
                      's2.more[1].title = "Deep"\n'
                      'print("{@1} {@2} {@3}", s.first.title, s.more[1].title, s2.more[1].title)\n'
                      'makeBook("ignored")\n'
                  )) == ["Dune x Copy changed", "Dune Copy Deep"]


def test_returned_string_arrays():
    assert run_ok('string[2] function pair() : ["left", "right"]\n' + main(
        'string[2] p = pair()\n'
        'p = pair()\n'
        'print("{@1} {@2} {@3}", p[0], p[1], pair()[0])\n'
        'pair()\n'
    )) == ["left right left"]


def test_early_exits_free_their_strings():
    assert run_ok(
        'string function scan(string[] words)\n'
        '    for i in range(0, len(words))\n'
        '        string w = words[i]\n'
        '        if w == "stop"\n'
        '            return "stopped"\n'
        '        if w == "skip"\n'
        '            continue\n'
        '        if w == "end"\n'
        '            break\n'
        '    return "done"\n'
        + main(
            'print("{@1}", scan(["a", "skip", "stop", "b"]))\n'
            'print("{@1}", scan(["end", "stop"]))\n'
            'print("{@1}", scan(["a"]))\n'
        )) == ["stopped", "done", "done"]


def test_temporaries_in_conditions_and_loops():
    assert run_ok(ECHO + main(
        'int n = 0\n'
        'while echo("go") == "go" and n < 3\n'
        '    string inner = echo("loop")\n'
        '    n = n + 1\n'
        '    if n == 2\n'
        '        continue\n'
        'print("n = {n}")\n'
        'if n > 5 and echo("x") == "x"\n'
        '    print("no")\n'
        'if n < 5 or echo("y") == "y"\n'
        '    print("short-circuit ok")\n'
    )) == ["n = 3", "short-circuit ok"]


def test_lambdas_and_const_strings():
    assert run_ok(ECHO + main(
        '(string) : string f = func(string x) : echo(x)\n'
        'print("{@1}", f("lambda"))\n'
        'const string fixed = echo("const")\n'
        'print("{fixed}")\n'
    )) == ["lambda", "const"]


def test_comparisons():
    assert run_ok(ECHO + main(
        'string a = echo("apple")\n'
        'print("{@1} {@2} {@3} {@4}", a == "apple", a != "apple", a < "banana", "b" > "a")\n'
        'print("{@1} {@2}", "abc" < "abd", "ab" < "abc")\n'
    )) == ["true false true true", "true true"]


def test_named_arguments_and_order_with_strings():
    assert run_ok(BOOK + ECHO + main(
        'Book b = Book(tags = [echo("t1"), "t2"], title = echo("Named"))\n'
        'print("{@1} {@2} {@3}", b.title, b.tags[0], b.tags[1])\n'
    )) == ["Named t1 t2"]


def test_changing_a_struct_parameter_never_touches_the_caller():
    assert run_ok(BOOK +
                  'Book function retag(Book b)\n'
                  '    b.title = "inside"\n'
                  '    b.tags[1] = "new"\n'
                  '    return b\n'
                  + main(
                      'Book mine = Book("mine", ["a", "b"])\n'
                      'Book other = retag(mine)\n'
                      'print("{@1} {@2} {@3} {@4}", mine.title, mine.tags[1], other.title, other.tags[1])\n'
                  )) == ["mine b inside new"]


# ============================================================
# 18.3.2 - String operations
# ============================================================

def run_error(source: str) -> str:
    """Compile and run a program expected to stop with a run-time error; return stderr."""
    exit_code, stdout, stderr = compile_and_run(source)
    assert exit_code == 1, f"expected a run-time error, got exit {exit_code}: {stdout}{stderr}"
    return stderr


def test_join_codegen_and_cleanup():
    c_code = generate_c(main('string a = "x"\nstring b = a + "y" + a'))
    assert 'fusion_string b = fusion_str_concat((fusion_tmp_' in c_code
    assert 'fusion_str_free(&fusion_tmp_' in c_code


def test_string_operations_end_to_end():
    assert run_ok(ECHO + main(
        'string a = "Hello"\n'
        'string b = a + ", " + "World" + \'!\'\n'
        'print("{b} {@1}", len(b))\n'
        'print("{@1}{@2}{@3}", b[0], b[len(b) - 1], \'!\' + a)\n'
        'print("[{@1}] {@2} {@3} {@4}", substring(b, 7, 5), contains(b, "World"), indexOf(b, "o"), indexOf(b, "z"))\n'
        'print("{@1} {@2}", startsWith(b, "Hell"), endsWith(echo(b), "!"))\n'
        'print("[{@1}] [{@2}] [{@3}]", toUpper(a), toLower("MiXeD"), trim("  padded \t"))\n'
    )) == ["Hello, World! 13", "H!!Hello", "[World] true 4 -1", "true true", "[HELLO] [mixed] [padded]"]


def test_conversions_end_to_end():
    assert run_ok(main(
        'print("{@1} {@2} {@3} {@4} {@5}", toString(42), toString(2.5), toString(true), toString(\'c\'), toString("s"))\n'
        'int n = toInt("-123")\n'
        'float f = toFloat("2.75")\n'
        'print("{@1} {@2}", n + 1, f)\n'
        'print("{@1} {@2} {@3} {@4} {@5}", isInt("12x"), isInt("2147483647"), isInt("2147483648"), isFloat("1e3"), isFloat(""))\n'
    )) == ["42 2.5 true c s", "-122 2.750000", "false true false true false"]


def test_building_a_string_in_a_loop_is_leak_free():
    assert run_ok(main(
        'string built = ""\n'
        'for i in range(0, 5)\n'
        '    built = built + toString(i) + ","\n'
        'print("{built}")\n'
    )) == ["0,1,2,3,4,"]


@pytest.mark.parametrize("statement, message", [
    ('char c = "abc"[5]', "index 5 is outside the string (length 3)"),
    ('char c = "abc"[-1]', "index -1 is outside the string (length 3)"),
    ('int n = toInt("12x")', "'12x' is not a whole number (check with isInt first)"),
    ('int n = toInt("99999999999")', "'99999999999' is not a whole number"),
    ('float f = toFloat("nan")', "'nan' is not a number (check with isFloat first)"),
    ('string s = substring("abc", 2, 5)', "substring(start 2, count 5) is outside the string (length 3)"),
])
def test_run_time_errors(statement, message):
    stderr = run_error(main(f'print("before")\n{statement}\nprint("after")'))
    assert "Runtime error at test.fusion:3: " + message in stderr


@pytest.mark.parametrize("body, message", [
    ('string s = "a" + 5', "Can't join a string and int with '+' - use interpolation"),
    ('string s = "a"\ns[0] = \'b\'', "A string can't be changed in place yet (Task 17)"),
    ('int n = len(5)', "Function 'len' expects an array, a string or bytes, got int"),
    ('string t = toString([1])', "Function 'toString' expects a single value"),
    ('char c = "abc"["x"]', "String index must be int, got string"),
    ('string s = substring("abc", 1)', "Function 'substring' expects 3 argument(s), got 2"),
    ('string s = trim(substring = "a")', "Named argument 'substring' can't be used when calling built-in"),
])
def test_string_operation_errors(body, message):
    assert message in errors_of(main(body))


def test_own_function_may_replace_a_string_built_in():
    """Since Task 18.3.6 a program's own function replaces a library built-in of the same
    name (see tests/test_string_library.py)."""
    assert run_ok('string function trim(string s) : "[" + s + "]"\n' + main('print(trim(" x "))')) \
        == ["[ x ]"]


# ============================================================
# 18.3.2b - Unicode by default
# ============================================================

def run_utf8(source: str) -> list:
    """Like run_ok, for output containing non-ASCII text."""
    exit_code, stdout, stderr = compile_and_run(source)
    assert exit_code == 0, f"exit {exit_code}: {stderr}"
    return stdout.splitlines()


def test_lengths_in_characters_and_bytes():
    assert run_utf8(main(
        'print("{@1} {@2}", len("caf\u00e9"), lenb("caf\u00e9"))\n'
        'print("{@1} {@2}", len("\u65e5\u672c"), lenb("\u65e5\u672c"))\n'
        'print("{@1} {@2}", len("plain"), lenb("plain"))\n'
    )) == ["4 5", "2 6", "5 5"]


def test_indexing_and_substring_by_character():
    assert run_utf8(main(
        'string jp = "\u65e5\u672c\u8a9e"\n'
        'print("{@1} {@2}", charCode(jp[0]), charCode(jp[2]))\n'
        'print("{@1}", lenb(substring(jp, 1, 2)))\n'
        'print("{@1}", indexOf("a\u00f1ob", "o"))\n'
    )) == ["26085 35486", "6", "2"]


def test_unicode_chars_join_and_convert():
    assert run_utf8(main(
        'char e = \'\u00e9\'\n'
        'string s = "caf" + e\n'
        'print("{@1} {@2} {@3} {@4}", len(s), lenb(s), charCode(e), s == "caf\u00e9")\n'
        'print("{@1} {@2}", lenb(toString(e)), charCode(fromCharCode(26085)))\n'
    )) == ["4 5 233 true", "2 26085"]


def test_encoding_helpers():
    assert run_utf8(main(
        'print("{@1} {@2}", isAscii("caf\u00e9"), isAscii("plain"))\n'
        'print("[{@1}]", asciiOnly("caf\u00e9 \u65e5", \'?\'))\n'
        'print("{@1} {@2}", byteAt("\u00e9", 0), byteAt("\u00e9", 1))\n'
    )) == ["false true", "[caf? ?]", "195 169"]


def test_printing_unicode():
    exit_code, stdout, _ = compile_and_run(main('char k = \'\u65e5\'\nprint("{@1}-{k}", "\u00e9")'))
    assert exit_code == 0
    assert stdout.strip() == '\u00e9-\u65e5'


def test_non_ascii_literals_carry_their_character_count():
    c_code = generate_c(main('string s = "caf\u00e9"\nchar c = \'\u00e9\''))
    assert 'FUSION_STRU("caf\u00e9", 4)' in c_code
    assert 'fusion_char c = ((fusion_char)0xE9);' in c_code


@pytest.mark.parametrize("statement, message", [
    ('char c = "ab"[2]', "index 2 is outside the string (length 2)"),
    ('char c = "\u65e5"[1]', "index 1 is outside the string (length 1)"),
    ('char c = fromCharCode(55296)', "55296 is not a Unicode character code"),
    ('int b = byteAt("\u00e9", 2)', "byte 2 is outside the string (2 bytes)"),
])
def test_unicode_run_time_errors(statement, message):
    assert message in run_error(main(f'print("before")\n{statement}'))


def test_ascii_encoding_rejects_non_ascii_text():
    from src.config import StringsConfig
    ast = parse(main('string s = "caf\u00e9"\nchar c = \'\u00e9\''))
    analyzer = __import__('src.semantic', fromlist=['SemanticAnalyzer']).SemanticAnalyzer(
        strings_config=StringsConfig(encoding='ascii'))
    assert not analyzer.analyze(ast)
    message = '\n'.join(str(e) for e in analyzer.get_errors())
    assert 'String literal contains U+00E9, but the project uses ascii encoding' in message
    assert 'Char literal contains U+00E9' in message


def test_ascii_encoding_makes_char_one_byte():
    from src.codegen import CCodeGenerator
    analyzer, ast, ok = analyze(main('string s = "abc"\nchar c = s[0]'))
    c_code = CCodeGenerator(encoding='ascii').generate(ast)
    assert '#define FUSION_ASCII 1' in c_code



# ============================================================
# 18.3.3 - Interpolated strings as values, format()
# ============================================================

def test_interpolated_string_is_a_value_anywhere():
    assert run_ok(ECHO + BOOK +
                  'string function label(string name, int n)\n'
                  '    return "{name} #{n}"\n'
                  + main(
                      'int x = 5\n'
                      'string s = "x is {x}"\n'
                      'print(s)\n'
                      'print(echo("echo {x}"))\n'
                      'print(label("item", 7))\n'
                      'Book b = Book("title {x}")\n'
                      'print(b.title)\n'
                      's = s + " and " + "x again {x}"\n'
                      'print("{@1} {@2}", s, len("{x}{x}"))\n'
                  )) == ["x is 5", "echo 5", "item #7", "title 5", "x is 5 and x again 5 2"]


def test_interpolation_formats_each_type():
    assert run_ok(main(
        'int i = 3\nfloat f = 1.5\nbool b = true\nchar c = \'z\'\nstring s = "str"\n'
        'string all = "{i}|{f}|{b}|{c}|{s}|100%"\n'
        'print(all)\n'
    )) == ["3|1.500000|true|z|str|100%"]


def test_format_returns_what_print_would_print():
    assert run_ok(ECHO + main(
        'string name = "Ada"\n'
        'string a = format("{@2}, {@1}!", "World", "Hello")\n'
        'string b = format("{name} is {@1}", 36)\n'
        'string c = format("plain")\n'
        'print("{@1}|{@2}|{@3}", a, b, c)\n'
        'print(format("{@1}{@1}", echo("twice")))\n'
    )) == ["Hello, World!|Ada is 36|plain", "twicetwice"]


def test_interpolation_in_a_loop_is_leak_free():
    assert run_ok(main(
        'string log = ""\n'
        'for i in range(0, 4)\n'
        '    log = log + "[{i}]"\n'
        'print(log)\n'
    )) == ["[0][1][2][3]"]


def test_interpolated_value_codegen():
    c_code = generate_c(main('int x = 1\nstring s = "x={x}"'))
    assert 'fusion_string s = fusion_str_format("x=%d", x);' in c_code


@pytest.mark.parametrize("body, message", [
    ('string s = "{@1}"', "{@1}-style placeholders only work in the text given to print(...) or format(...)"),
    ('string s = format("{@2}", 1)', "{@2} has no matching argument - format() was given 1 argument(s)"),
    ('string s = format("plain", 1)', "format() was given 1 argument(s) after its text"),
    ('int[] a = [1]\nstring s = "{a}"', "Can't print a whole int[1] value"),
])
def test_interpolation_errors(body, message):
    assert message in errors_of(main(body))


# ============================================================
# 18.3.4 / 18.3.4b - Any length by default; [strings] max_length for constrained devices
# ============================================================

def run_with_limit(source: str, limit):
    """Compile with a [strings] max_length (None = "max") under the leak check, run, and
    return (exit code, stdout lines, stderr)."""
    from src.codegen import CCodeGenerator
    from src.semantic import SemanticAnalyzer
    from src.config import StringsConfig
    ast = parse(source)
    analyzer = SemanticAnalyzer(structs_config=StructsConfig(string_warn_length=0),
                                strings_config=StringsConfig(max_length=limit))
    assert analyzer.analyze(ast), analyzer.get_errors()
    c_code = CCodeGenerator(max_length=limit).generate(ast)
    with tempfile.TemporaryDirectory() as tmp:
        c_file, exe = os.path.join(tmp, 'limit.c'), os.path.join(tmp, 'limit.exe')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        build = subprocess.run(['gcc', '-DFUSION_LEAK_CHECK', '-Wall', '-Wextra', c_file, '-o', exe],
                               capture_output=True, text=True)
        assert build.returncode == 0, build.stderr
        assert 'warning' not in build.stderr.replace('fusion_len_', ''), build.stderr
        result = subprocess.run([exe], capture_output=True, text=True, encoding='utf-8')
        return result.returncode, result.stdout.splitlines(), result.stderr


NOTE = 'struct Note\n    string text\n    string[2] tags\n\n'


def test_strings_have_no_limit_by_default():
    code, out, _ = run_with_limit(NOTE + main(
        'string big = ""\n'
        'for i in range(0, 1000)\n'
        '    big = big + "0123456789"\n'
        'Note n = Note(big)\n'
        'Note copy = n\n'
        'print("{@1} {@2} {@3}", len(big), len(n.text), len(copy.text))\n'
    ), None)
    assert (code, out) == (0, ["10000 10000 10000"])


def test_no_limit_means_no_checking_code():
    c_code = generate_c(main('string s = "a" + "b"'))
    assert '#define FUSION_MAX_LENGTH' not in c_code
    assert 'fusion_at = "' not in c_code


def test_within_the_limit_runs_normally():
    code, out, err = run_with_limit(ECHO + NOTE + main(
        'Note n = Note(echo("abc"), [echo("12345"), "x"])\n'
        'print("{@1} {@2}", n.text, n.tags[0])\n'
    ), 5)
    assert (code, out, err) == (0, ["abc 12345"], "")


@pytest.mark.parametrize("statement", [
    'string s = echo("abcdef") + echo("ghijk")',         # call results joined
    'string s = "abcdef" + "ghijk"',                     # source text joined
    'int n = 123456\nstring s = "n={n}{n}"',              # interpolation
    'Note n = Note(echo("abcdef") + "ghijk")',           # into a struct field
])
def test_a_longer_string_is_a_run_time_error_never_a_cut(statement):
    code, out, err = run_with_limit(ECHO + NOTE + main(f'print("before")\n{statement}\nprint("after")'), 10)
    assert code == 1 and out == ["before"]
    assert "Runtime error at test.fusion:" in err
    assert "characters is longer than max_length 10 ([strings] in fusion.toml)" in err


def test_limit_counts_characters_not_bytes():
    code, out, _ = run_with_limit(ECHO + main(
        'string s = echo("\\u00e9\\u00e9\\u00e9")\n'
        'print("{@1} {@2}", len(s), lenb(s))\n'
    ), 3)
    assert (code, out) == (0, ["3 6"])


def test_source_text_over_the_limit_is_a_compile_error():
    from src.semantic import SemanticAnalyzer
    from src.config import StringsConfig
    analyzer = SemanticAnalyzer(strings_config=StringsConfig(max_length=5))
    assert not analyzer.analyze(parse(main('string s = "abcdefgh"')))
    assert any("String has 8 characters, more than the project's max_length of 5" in str(e)
               for e in analyzer.get_errors())
