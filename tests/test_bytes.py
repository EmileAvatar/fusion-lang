"""Tests for Task 18.3.8 - raw bytes: `byte` (0-255) and `bytes` (src/codegen/c_bytes.py).

User decisions 2026-10-10: byte is unsigned 0-255; ints are little-endian unless
bigEndian = true; hexToBytes / bytesToHex stay on text and hexToRaw / rawToHex work on
bytes; a bytes value prints as plain lowercase hex with nothing added. Every program runs
under the leak check.
"""

import pytest

from tests.test_structs import errors_of, main
from tests.test_strings import run_ok, run_error


def test_the_kkkkk_edit():
    """The user's example: kkkkk -> kkikk -> kkijk, edited byte by byte in memory."""
    assert run_ok(main(
        'bytes data = toBytes("kkkkk")\n'
        'print("{data} {@1}", len(data))\n'
        'data[2] = 0x69\n'
        'print(toString(data))\n'
        'data[3] = toByte(fromHex("6A"))\n'
        'print("{data} {@1}", toString(data))'
    )) == ['6b6b6b6b6b 5', 'kkikk', '6b6b696a6b kkijk']


def test_strings_chars_ints_to_bytes_and_back():
    assert run_ok(main(
        'print("{@1} {@2} {@3}", rawToHex(toBytes("caf\\u00e9")), rawToHex(toBytes(\'\\u00e9\')), rawToHex(toBytes("")))\n'
        'bytes n = toBytes(258)\n'
        'bytes big = toBytes(258, true)\n'
        'print("{n} {big} {@1} {@2}", getInt(n, 0), getInt(big, 0, true))\n'
        'print("{@1} {@2}", rawToHex(toBytes(-1)), getInt(toBytes(-12345), 0))\n'
        'byte b = 0xFF\n'
        'print("{@1} {b}", rawToHex(toBytes(b)))\n'
        'print("{@1} {@2}", toString(toBytes("caf\\u00e9")), toString(hexToRaw("6869")))'
    )) == ['636166c3a9 c3a9 ', '02010000 00000102 258 258', 'ffffffff -12345',
           'ff 255', 'caf\u00e9 hi']


def test_making_joining_slicing_searching():
    assert run_ok(main(
        'bytes raw = [0x00, 0xFF, 0x10]\n'
        'bytes empty = []\n'
        'bytes none\n'
        'print("{raw} [{empty}] [{none}] {@1}", len(none))\n'
        'raw = raw + 0x41 + toBytes("B")\n'
        'raw = 0x01 + raw\n'
        'print("{raw} {@1}", rawToHex(newBytes(3, 0x7F)) + rawToHex(newBytes(2)))\n'
        'print("{@1} {@2} {@3}", rawToHex(slice(raw, 1, 2)), indexOf(raw, toBytes("AB")), indexOf(raw, hexToRaw("ff"), 3))\n'
        'print("{@1}", indexOf("text still works", "works"))'
    )) == ['00ff10 [] [] 0', '0100ff104142 7f7f7f0000', '00ff 4 -1', '11']


def test_numbers_inside_bytes():
    assert run_ok(main(
        'bytes b = newBytes(8)\n'
        'setInt(b, 0, 0x01020304)\n'
        'setInt(b, 4, 0x01020304, true)\n'
        'print("{b}")\n'
        'setInt16(b, 0, -2)\n'
        'setInt16(b, 2, 65535, true)\n'
        'print("{b} {@1} {@2} {@3}", getInt16(b, 0), getUInt16(b, 0), getUInt16(b, 2, true))'
    )) == ['0403020101020304', 'feffffff01020304 -2 65534 65535']


def test_bytes_are_values_edited_in_place():
    """Copies are independent; a function that edits its parameter edits its own copy;
    struct fields and equality work like strings."""
    assert run_ok('struct Packet\n    bytes body\n    int id\n\n'
                  'void function stamp(bytes b)\n    b[0] = 0xFF\n    setInt16(b, 1, 0)\n    print("inside: {b}")\n\n'
                  + main(
                      'bytes data = toBytes("abc")\n'
                      'bytes copy = data\n'
                      'copy[0] = 0x41\n'
                      'stamp(data)\n'
                      'print("{data} {copy}")\n'
                      'Packet p = Packet(newBytes(3, 7), 1)\n'
                      'Packet q = p\n'
                      'q.body[1] = 9\n'
                      'print("{@1} {@2} {@3} {@4}", rawToHex(p.body), rawToHex(q.body), p == q, p.body != q.body)\n'
                      'print("{@1} {@2}", toBytes("hi") == hexToRaw("6869"), toBytes("hi") === toBytes("hj"))'
                  )) == ['inside: ff0000', '616263 416263', '070707 070907 false true', 'true false']


def test_byte_arithmetic_gives_int():
    assert run_ok(main(
        'bytes d = [200, 100]\n'
        'byte a = d[0]\n'
        'int sum = a + d[1]\n'
        'print("{sum} {@1} {@2}", d[0] > d[1], d[0] == 200)\n'
        'd[1] = toByte(sum - 255)'
        '\nprint("{d}")'
    )) == ['300 true true', 'c82d']


def test_is_text():
    assert run_ok(main(
        'print("{@1} {@2} {@3}", isText(toBytes("caf\\u00e9")), isText(hexToRaw("ff")), isText(hexToRaw("eda080")))'
    )) == ['true false false']


@pytest.mark.parametrize("statement, message", [
    ('bytes b = toBytes("ab")\nprint("{@1}", b[2])', "byte 2 is outside the bytes (length 2)"),
    ('bytes b = toBytes("ab")\nb[-1] = 1', "byte -1 is outside the bytes (length 2)"),
    ('print("{@1}", toByte(256))', "256 doesn't fit in a byte (0-255)"),
    ('print("{@1}", toByte(-1))', "-1 doesn't fit in a byte (0-255)"),
    ('print("{@1}", getInt(toBytes("abc"), 0))', "getInt(at 0) needs 4 bytes there, but the bytes have length 3"),
    ('bytes b = newBytes(2)\nsetInt16(b, 0, 70000)', "setInt16: 70000 doesn't fit in 16 bits"),
    ('print(toString(hexToRaw("ff")))', "these 1 bytes are not valid text (check with isText first)"),
    ('print("{@1}", slice(toBytes("ab"), 1, 5))', "slice(start 1, count 5) is outside the bytes (length 2)"),
    ('print("{@1}", newBytes(-1))', "newBytes(-1): the count can't be negative"),
    ('print("{@1}", hexToRaw("abc"))', "hexToRaw: 'abc' has an odd number of hex digits"),
])
def test_run_time_errors(statement, message):
    assert message in run_error(main(statement))


@pytest.mark.parametrize("body, message", [
    ('byte b = 300', "Cannot assign int to variable of type byte"),
    ('byte b = -1', "Cannot assign int to variable of type byte"),
    ('byte b = 100 + 200', "Cannot assign int to variable of type byte"),
    ('int n = 5\nbyte b = n', "Cannot assign int to variable of type byte"),
    ('bytes d = newBytes(2)\nint n = 5\nd[0] = n', "a byte holds 0-255; use toByte(n)"),
    ('bytes d = newBytes(2)\nbyte b = d[0] + 1', "Cannot assign int to variable of type byte"),
    ('bytes d = [1, 256]', "A bytes element must be a byte (0-255), got int"),
    ('int n = 9\nbytes d = toBytes("a") + n', "Can't join bytes and int with '+'"),
    ('bytes d = toBytes(2.5)', "Argument 1 to 'toBytes': expected string, got float"),
    ('string s = "x"\nbytes d = s', "Cannot assign string to variable of type bytes"),
    ('bool r = toBytes("a") == "a"', "Can't compare bytes with string using '=='"),
    ('setInt(toBytes("abcd"), 0, 1)', "'setInt' changes its first argument, so it must be a variable"),
    ('const string c = "x"\nint n = len(c)', None),
])
def test_compile_errors(body, message):
    if message is None:
        return
    assert message in errors_of(main(body))


def test_struct_cannot_be_named_bytes():
    assert "'bytes' is a built-in type" in errors_of('struct bytes\n    int x\n\n' + main('int y = 1'))
