"""Tests for Task 18.3.6 - the versatile string functions (src/codegen/c_strings.py).

Positions and counts are characters; letters are ASCII + Latin-1; "up to n" functions
clamp quietly; a negative count is a run-time error. Every program runs under the leak
check (see tests/test_end_to_end.py).
"""

import os
import subprocess
import tempfile

import pytest

from src.codegen.c_memory import RUNTIME_PRELUDE
from tests.test_structs import errors_of, main
from tests.test_strings import run_ok, run_error, ECHO


def show(*expressions: str) -> str:
    """A print statement showing each expression, separated by ` | `."""
    holes = ' | '.join(f'{{@{i + 1}}}' for i in range(len(expressions)))
    return f'print("{holes}", {", ".join(expressions)})'


@pytest.mark.parametrize("ascii_mode", [False, True])
def test_runtime_compiles_cleanly(ascii_mode):
    """The whole runtime - every string function - compiles with no warnings under
    -Wall -Wextra, in UTF-8 and in ascii mode (fusion_char is one byte there)."""
    with tempfile.TemporaryDirectory() as tmp:
        c_file = os.path.join(tmp, 'rt.c')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(('#define FUSION_ASCII 1\n' if ascii_mode else '')
                    + '#include <stdarg.h>\n#include <stdbool.h>\n#include <stdint.h>\n'
                    '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n'
                    + RUNTIME_PRELUDE + 'int main(void) { return 0; }\n')
        build = subprocess.run(['gcc', '-Wall', '-Wextra', '-c', c_file, '-o',
                                os.path.join(tmp, 'rt.o')], capture_output=True, text=True)
        assert build.returncode == 0 and 'warning' not in build.stderr, build.stderr


# ============================================================
# 18.3.6a - Inspect, search, extract
# ============================================================

def test_inspect():
    assert run_ok(main(
        show('isEmpty("")', 'isEmpty(" ")', 'isBlank(" \\t\\n")', 'isBlank("")', 'isBlank(" x ")')
        + '\n' + show('isDigits("0123")', 'isDigits("")', 'isDigits("12a")', 'isDigits("-1")')
        + '\n' + show('isLetters("Caf\\u00e9")', 'isLetters("Stra\\u00dfe")', 'isLetters("")',
                      'isLetters("a b")', 'isLetters("x2")', 'isLetters("\\u65e5")')
        + '\n' + show('countOf("aaaa", "aa")', 'countOf("banana", "a")', 'countOf("abc", "")',
                      'countOf("\\u00e9t\\u00e9", "\\u00e9")')
    )) == ['true | false | true | true | false', 'true | false | false | false',
           'true | true | false | false | false | false', '2 | 3 | 0 | 2']


def test_search_counts_characters():
    assert run_ok(main(
        'string s = "caf\\u00e9 au lait"\n'
        + show('indexOf(s, "a")', 'indexOf(s, "a", 2)', 'indexOf(s, "a", 100)', 'indexOf(s, "a", -5)',
               'indexOf(s, "z")', 'lastIndexOf(s, "a")', 'lastIndexOf(s, "\\u00e9")', 'lastIndexOf(s, "z")')
        + '\n' + show('containsAny(s, "xyz\\u00e9")', 'containsAny(s, "xyz")', 'containsAny(s, "")')
    )) == ['1 | 5 | -1 | 1 | -1 | 9 | 3 | -1', 'true | false | false']


def test_left_and_right_clamp():
    assert run_ok(ECHO + main(
        'string s = echo("caf\\u00e9!")\n'
        'print("[{@1}] [{@2}] [{@3}] [{@4}] [{@5}]", left(s, 4), right(s, 2), left(s, 99), right(s, 99), left(s, 0))'
    )) == ['[caf\u00e9] [\u00e9!] [caf\u00e9!] [caf\u00e9!] []']


@pytest.mark.parametrize("call, message", [
    ('left("abc", -1)', "left(-1): the count can't be negative"),
    ('right("abc", -2)', "right(-2): the count can't be negative"),
])
def test_negative_counts_are_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))


def test_optional_argument_counts():
    errors = errors_of(main('int a = indexOf("abc")\nint b = indexOf("abc", "b", 1, 2)'))
    assert "Function 'indexOf' expects 2 to 3 arguments, got 1" in errors
    assert "Function 'indexOf' expects 2 to 3 arguments, got 4" in errors


def test_own_function_replaces_a_library_built_in():
    """left, right, ... are everyday names: a program's own function or struct with that
    name replaces the built-in; a local variable just shadows it."""
    assert run_ok('int function right(int a)\n    return a + 1\n\nstruct left\n    int x\n\n' + main(
        'int remove = 2\n'
        'left l = left(right(remove))\n'
        'print("{@1}", l.x)'
    )) == ['3']


def test_core_built_ins_cannot_be_replaced():
    assert "Duplicate declaration of 'print'" in errors_of('void function print(string s)\n    return\n\n'
                                                            + main('int x = 1'))


# ============================================================
# 18.3.6b - Change
# ============================================================

def test_replace_insert_remove():
    assert run_ok(ECHO + main(
        'string s = echo("a-b-c")\n'
        'print("[{@1}] [{@2}] [{@3}] [{@4}]", replace(s, "-", "+="), replaceFirst(s, "-", ""), replace(s, "", "x"), replace(s, "z", "y"))\n'
        'print("[{@1}] [{@2}] [{@3}]", insert("caf\u00e9", 3, "-"), insert("ab", 2, "!"), insert("", 0, "x"))\n'
        'print("[{@1}] [{@2}] [{@3}]", remove("caf\u00e9 au", 2, 3), remove("abc", 0, 3), remove("abc", 3, 0))\n'
        's = replace(s, "b", s)\n'
        'print(s)'
    )) == ['[a+=b+=c] [ab-c] [a-b-c] [a-b-c]', '[caf-\u00e9] [ab!] [x]', '[caau] [] [abc]', 'a-a-b-c-c']


def test_repeat_reverse_trim():
    assert run_ok(main(
        'print("[{@1}] [{@2}] [{@3}]", repeat("ab", 3), repeat("ab", 0), repeat("", 5))\n'
        'print("[{@1}] [{@2}] [{@3}]", reverse("caf\u00e9"), reverse(""), reverse("\u65e5\u672c!"))\n'
        'print("[{@1}] [{@2}]", trimStart("  x  "), trimEnd("  x \t\n"))'
    )) == ['[ababab] [] []', '[\u00e9fac] [] [!\u672c\u65e5]', '[x  ] [  x]']


def test_case_covers_latin_1():
    """ASCII + Latin-1 (user decision): toUpper / toLower now change accented letters too;
    capitalize and toTitle change only first letters, so acronyms survive."""
    assert run_ok(main(
        'print("{@1} {@2}", toUpper("caf\u00e9 \u00fcber \u00ff\u00df"), toLower("CAF\u00c9 \u0178"))\n'
        'print("[{@1}] [{@2}] [{@3}]", capitalize("  hello world"), capitalize("\u00e9t\u00e9"), capitalize("42"))\n'
        'print("[{@1}] [{@2}]", toTitle("hello  big\tworld"), toTitle("NASA and jean-luc"))'
    )) == ['CAF\u00c9 \u00dcBER \u0178\u00df caf\u00e9 \u00ff',
           '[  Hello world] [\u00c9t\u00e9] [42]',
           '[Hello  Big\tWorld] [NASA And Jean-luc]']


@pytest.mark.parametrize("call, message", [
    ('insert("abc", 4, "x")', "insert(index 4) is outside the string (length 3)"),
    ('insert("abc", -1, "x")', "insert(index -1) is outside the string"),
    ('remove("abc", 1, 3)', "remove(start 1, count 3) is outside the string (length 3)"),
    ('repeat("ab", -1)', "repeat(-1): the count can't be negative"),
    ('repeat("abcdefgh", 1000000000)', "repeat: the result would be longer than"),
])
def test_change_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))


# ============================================================
# 18.3.6c - Padding & alignment
# ============================================================

def test_padding_and_center():
    assert run_ok(ECHO + main(
        'print("[{@1}] [{@2}] [{@3}]", padLeft("7", 3, \'0\'), padLeft("ab", 5), padLeft("abcdef", 3))\n'
        'print("[{@1}] [{@2}] [{@3}]", padRight("ab", 5), padRight("ab", 4, \'.\'), padRight(echo("x"), 0))\n'
        'print("[{@1}] [{@2}] [{@3}]", center("ab", 6), center("ab", 5, \'*\'), center("caf\u00e9", 6, \'\u00b7\'))'
    )) == ['[007] [   ab] [abcdef]', '[ab   ] [ab..] [x]', '[  ab  ] [*ab**] [\u00b7caf\u00e9\u00b7]']


def test_truncate_adds_nothing():
    """User decision 2026-10-10: truncate returns only the kept characters - no "..."."""
    assert run_ok(main(
        'print("[{@1}] [{@2}] [{@3}]", truncate("Hello world", 8), truncate("Hello", 8), truncate("Hello", 5))\n'
        'print("[{@1}] [{@2}]", truncate("Hello", 0), truncate("caf\u00e9 au lait", 4))'
    )) == ['[Hello wo] [Hello] [Hello]', '[] [caf\u00e9]']


@pytest.mark.parametrize("call, message", [
    ('padLeft("ab", -1)', "padLeft(width -1): the width can't be negative"),
    ('center("ab", -3, \'*\')', "center(width -3): the width can't be negative"),
    ('truncate("ab", -1)', "truncate(width -1): the width can't be negative"),
])
def test_padding_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))


def test_padding_argument_types():
    errors = errors_of(main('string a = padLeft("x", 3, "0")\nstring b = truncate("x", 3, "...")'))
    assert "expected char, got string" in errors
    assert "Function 'truncate' expects 2 argument(s), got 3" in errors


# ============================================================
# 18.3.6d-1 - Hex, binary, octal (two's complement, C# style)
# ============================================================

def test_to_hex_binary_octal_from_int_or_text():
    assert run_ok(ECHO + main(
        'print("{@1} {@2} {@3} {@4}", toHex(255), toHex("255"), toBinary(5), toOctal(8))\n'
        'print("{@1} {@2} {@3}", toHex(255, 4), toBinary(5, 8), toHex(echo("4096"), 2))\n'
        'print("{@1} {@2} {@3}", toHex(-1), toOctal(-1), toHex(-255))\n'
        'print("{@1}", toBinary(-1))\n'
        'print("{@1} {@2} {@3} {@4}", toBase(255, 16), toBase(-255, 16), toBase(35, 36), toBase("10", 2, 8))'
    )) == ['ff ff 101 10', '00ff 00000101 1000', 'ffffffff 37777777777 ffffff01',
           '1' * 32, 'ff -ff z 00001010']


def test_from_hex_binary_octal_and_parse_int():
    assert run_ok(main(
        'print("{@1} {@2} {@3} {@4}", fromHex("ff"), fromHex("0xFF"), fromHex("-ff"), fromHex("ffffffff"))\n'
        'print("{@1} {@2} {@3} {@4}", fromBinary("0b101"), fromOctal("0o17"), fromHex("80000000"), fromHex(toHex(-12345)))\n'
        'print("{@1} {@2} {@3}", parseInt("z", 36), parseInt("-101", 2), parseInt("42", 10))\n'
        'print("{@1} {@2} {@3} {@4}", isInt("ff", 16), isInt("fg", 16), isInt("ffffffff", 16), isInt("4294967295"))\n'
        'print(toString(fromHex("ff")))'
    )) == ['255 255 -255 -1', '5 15 -2147483648 -12345', '35 -5 42',
           'true false true false', '255']


def test_bytes_as_hex():
    assert run_ok(main(
        'print("{@1} {@2} {@3}", bytesToHex("Hi"), bytesToHex("caf\u00e9"), bytesToHex(""))\n'
        'print("[{@1}] [{@2}]", hexToBytes("4869"), hexToBytes("636166C3A9"))'
    )) == ['4869 636166c3a9 ', '[Hi] [caf\u00e9]']


@pytest.mark.parametrize("call, message", [
    ('fromHex("fg")', "'fg' is not a base-16 whole number that fits in an int"),
    ('fromHex("1ffffffff")', "'1ffffffff' is not a base-16 whole number"),
    ('fromBinary("")', "'' is not a base-2 whole number"),
    ('parseInt("99999999999", 10)', "is not a base-10 whole number"),
    ('parseInt("1", 37)', "parseInt: base 37 is not between 2 and 36"),
    ('toBase(5, 1)', "toBase: base 1 is not between 2 and 36"),
    ('toHex("12x")', "'12x' is not a whole number"),
    ('toHex(5, -1)', "toHex(width -1): the width can't be negative"),
    ('hexToBytes("abc")', "hexToBytes: 'abc' has an odd number of hex digits"),
    ('hexToBytes("zz")', "hexToBytes: 'zz' is not hex text"),
    ('hexToBytes("ff")', "hexToBytes: the bytes of 'ff' are not valid text"),
    ('hexToBytes("eda080")', "the bytes of 'eda080' are not valid text"),   # a surrogate
])
def test_base_run_time_errors(call, message):
    assert message in run_error(main(f'print("{{@1}}", {call})'))


def test_to_hex_type_errors():
    errors = errors_of(main('string a = toHex(2.5)\nstring b = toHex(true)\nint c = fromHex(255)'))
    assert "Argument 1 to 'toHex': expected int, got float" in errors
    assert "Argument 1 to 'toHex': expected int, got bool" in errors
    assert "Argument 1 to 'fromHex': expected string, got int" in errors


def test_hex_binary_octal_literals_and_underscores():
    assert run_ok(main(
        'int mask = 0xFF\n'
        'int bits = 0b1111_0000\n'
        'print("{@1} {@2} {@3} {@4}", mask, bits, 0o17, 1_000_000)\n'
        'print("{@1} {@2} {@3}", 0xFFFFFFFF, 0x80000000, 2.5_0 + 1_0.0)\n'
        'print("{@1}", 0xff + 0XA - 0x7FFFFFFF)'
    )) == ['255 240 15 1000000', '-1 -2147483648 12.500000', str(255 + 10 - 0x7FFFFFFF)]


@pytest.mark.parametrize("literal, message", [
    ('0x', "A hex literal needs digits after '0x'"),
    ('0b102', "'2' is not a binary digit in this literal"),
    ('0o78', "'8' is not an octal digit"),
    ('0x1_0000_0000', "is larger than 32 bits"),
    ('0xFG', "'G' is not a hex digit"),
])
def test_bad_based_literals(literal, message):
    from src.lexer import Lexer
    lexer = Lexer(main(f'int x = {literal}'), 'test.fusion')
    try:
        lexer.tokenize()
        found = '\n'.join(str(e) for e in lexer.diagnostics.errors)
    except Exception as e:  # the lexer may raise on the first error
        found = str(e)
    assert message in found


# ============================================================
# 18.3.6d-2 - formatNumber: Excel/.NET style and printf style
# ============================================================

def test_format_number_excel_style():
    assert run_ok(main(
        'print("{@1} | {@2} | {@3}", formatNumber(1234.5, "#,##0.00"), formatNumber(7, "000"), formatNumber(1234567, "#,##0"))\n'
        'print("{@1} | {@2} | {@3}", formatNumber(2.675, "0.00"), formatNumber(-2.5, "0"), formatNumber(-0.004, "0.00"))\n'
        'print("{@1} | {@2} | {@3}", formatNumber(1234.5, "$#,##0.00"), formatNumber(72.25, "0.0 kg"), formatNumber(0.256, "0.0%"))\n'
        'print("{@1} | {@2} | {@3}", formatNumber(0.5, "#.00"), formatNumber(3.1, "0.0##"), formatNumber(3.14159, "0.0##"))\n'
        'print("{@1} | {@2} | [{@3}]", formatNumber(100, "#,###"), formatNumber(999.996, "#,##0.00"), formatNumber(0, "#"))'
    )) == ['1,234.50 | 007 | 1,234,567', '2.68 | -3 | 0.00', '$1,234.50 | 72.3 kg | 25.6%',
           '.50 | 3.1 | 3.142', '100 | 1,000.00 | []']


def test_format_number_printf_style():
    assert run_ok(main(
        'print("{@1} | {@2} | {@3}", formatNumber(3.14159, "%.2f"), formatNumber(42, "%05d"), formatNumber(2.5, "%d"))\n'
        'print("[{@1}] | [{@2}] | {@3}", formatNumber(3.5, "%8.2f kg"), formatNumber(7, "%-4d|"), formatNumber(255, "%x"))\n'
        'print("{@1} | {@2} | {@3}", formatNumber(-1, "%X"), formatNumber(8, "%#o"), formatNumber(12345.678, "%.3e"))\n'
        'print("{@1} | {@2}", formatNumber(50, "%d%% done"), formatNumber(1, "%+d"))'
    )) == ['3.14 | 00042 | 3', '[    3.50 kg] | [7   |] | ff', 'FFFFFFFF | 010 | 1.235e+04',
           '50% done | +1']


@pytest.mark.parametrize("pattern, problem", [
    ('"%s"', "only the conversions d i f e E g G x X o are allowed"),
    ('"%n"', "only the conversions"),
    ('"%d and %d"', "more than one number conversion"),
    ('"%*d"', "'*' widths aren't allowed"),
    ('"%5000d"', "a width over 1000"),
    ('"%ld"', "only the conversions"),
    ('"%"', "a '%' at the end has no conversion letter"),
    ('"%% only"', "no number conversion such as %d or %.2f"),
    ('"abc"', "no 0 or # digit placeholder"),
    ('"0.0.0"', "more than one decimal point"),
    ('"0.0,0"', "a ',' after the decimal point"),
    ('"0x0"', "a character other than 0 # , . inside the number part"),
    ('"0.0000000000000000"', "more than 15 decimal places"),
])
def test_bad_patterns_are_compile_errors(pattern, problem):
    errors = errors_of(main(f'string s = formatNumber(1, {pattern})'))
    assert f'Invalid number pattern {pattern}: {problem}' in errors


def test_bad_pattern_built_at_run_time():
    assert 'invalid number pattern "%s": only the conversions' in run_error(main(
        'string p = "%" + "s"\nprint(formatNumber(1, p))'))


@pytest.mark.parametrize("call, message", [
    ('formatNumber(1.0 / 0.0, "0")', "formatNumber: the number isn't finite"),
    ('formatNumber(1000000000.0 * 1000000000.0 * 1000.0, "0.00")', "is too large for this pattern"),
    ('formatNumber(1000000.0 * 1000000.0, "%x")', "doesn't fit in an int for %x"),
])
def test_format_number_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))


# ============================================================
# 18.3.6e - Compare
# ============================================================

def test_ignore_case():
    assert run_ok(main(
        'print("{@1} {@2} {@3}", equalsIgnoreCase("Hello", "hELLO"), equalsIgnoreCase("CAF\u00c9", "caf\u00e9"), equalsIgnoreCase("a", "ab"))\n'
        'print("{@1} {@2} {@3} {@4}", compareIgnoreCase("apple", "BANANA"), compareIgnoreCase("B", "a"), compareIgnoreCase("x", "X"), compareIgnoreCase("ab", "a"))\n'
        'print("{@1}", "apple" < "BANANA")'
    )) == ['true true false', '-1 1 0 1', 'false']


def test_compare_natural():
    assert run_ok(main(
        'print("{@1} {@2} {@3}", compareNatural("file2", "file10"), compareNatural("file10", "file2"), compareNatural("file10", "file10"))\n'
        'print("{@1} {@2} {@3}", compareNatural("a2b10", "a2b9"), compareNatural("x007", "x7"), compareNatural("x7", "x007"))\n'
        'print("{@1} {@2} {@3}", compareNatural("v1.10", "v1.9"), compareNatural("File2", "file10"), compareNatural("File2", "file10", true))\n'
        'print("{@1} {@2}", compareNatural("10", "9z"), compareNatural("abc", "ab"))'
    )) == ['-1 1 0', '1 1 -1', '1 -1 -1', '1 1']
