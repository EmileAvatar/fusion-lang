"""Tests for masking - formatMask, digitsOnly, mask, maskEmail (design and the user's nine
decisions: the spec's "Masking" section, Task 18.3.6f).

Length is kept; the mask character is optional (default *); formatMask fills as far as it
fits; placeholders # A ? and a backslash for a literal; emails show the first character
(configurable); no phone or country formats - the developer supplies the pattern.
"""

import pytest

from tests.test_structs import errors_of, main
from tests.test_strings import run_ok, run_error


def test_format_mask():
    assert run_ok(main(
        'print("[{@1}] [{@2}]", formatMask("5551234567", "(###) ###-####"), formatMask("555-123-4567", "(###) ###-####"))\n'
        'print("[{@1}] [{@2}] [{@3}]", formatMask("55512", "(###) ###-####"), formatMask("555", "(###) ###-####"), formatMask("", "(###)"))\n'
        'print("[{@1}] [{@2}]", formatMask("5551234567999", "###-####"), formatMask("ab12", "AA-##"))\n'
        'print("[{@1}] [{@2}]", formatMask("1a2b", "#-#"), formatMask("x1", "?#"))\n'
        'print("[{@1}] [{@2}]", formatMask("12", "\\\\##\\\\A#"), formatMask("\\u00e9t\\u00e9", "A.A.A"))'
    )) == ['[(555) 123-4567] [(555) 123-4567]', '[(555) 12] [(555] []',
           '[555-1234] [ab-12]', '[1-2] [x1]', '[#1A2] [\u00e9.t.\u00e9]']


def test_digits_only():
    assert run_ok(main(
        'print("[{@1}] [{@2}] [{@3}]", digitsOnly("(555) 123-4567"), digitsOnly("abc"), digitsOnly("+27 82 555"))'
    )) == ['[5551234567] [] [2782555]']


def test_mask_keeps_the_length():
    assert run_ok(main(
        'string card = "4111111111111111"\n'
        'print("{@1} {@2}", mask(card, 0, 4), mask(card, 6, 4))\n'
        'print("{@1} {@2} {@3}", mask(card, 6, 4, \'X\'), mask("abc", 2, 2), mask("caf\\u00e9!", 1, 1, \'\\u00b7\'))\n'
        'print("{@1}", card.mask(0, 4))'
    )) == ['************1111 411111******1111', '411111XXXXXX1111 abc c\u00b7\u00b7\u00b7!',
           '************1111']


def test_mask_email():
    assert run_ok(main(
        'print("{@1} {@2}", maskEmail("alice@example.com"), maskEmail("alice.smith@example.com", 3))\n'
        'print("{@1} {@2} {@3}", maskEmail("al@x.io", 1, \'#\'), maskEmail("a@x.io"), maskEmail("nobody"))\n'
        'print("{@1}", "bob@host.org".maskEmail())'
    )) == ['a****@example.com ali********@example.com', 'a#@x.io a@x.io n*****', 'b**@host.org']


@pytest.mark.parametrize("call, message", [
    ('mask("abc", -1, 0)', "mask(-1, 0): the counts can't be negative"),
    ('maskEmail("a@b.c", -2)', "maskEmail(-2): the count can't be negative"),
])
def test_masking_run_time_errors(call, message):
    assert message in run_error(main(f'print({call})'))


def test_mask_character_must_be_a_char():
    assert "Argument 4 to 'mask': expected char, got string" in errors_of(
        main('string s = mask("abcd", 1, 1, "#")'))
