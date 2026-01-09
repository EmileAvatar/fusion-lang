"""Test suite for literal tokenization.

Tests integer, float, string (with interpolation), and character literals.
"""

import pytest
import json
from src.lexer.literals import (
    # Escape sequences
    ESCAPE_SEQUENCES,
    parse_escape_sequence,
    # Integers
    is_digit,
    parse_integer,
    # Floats
    parse_float,
    # Strings
    parse_string_interpolation,
    parse_string,
    # Characters
    parse_char,
    # Helpers
    is_literal_start,
    decode_string_parts,
    has_interpolation,
    get_plain_string,
)


class TestEscapeSequences:
    """Test escape sequence support."""

    def test_escape_sequence_table(self):
        """Verify escape sequence mappings."""
        assert ESCAPE_SEQUENCES['n'] == '\n'
        assert ESCAPE_SEQUENCES['t'] == '\t'
        assert ESCAPE_SEQUENCES['r'] == '\r'
        assert ESCAPE_SEQUENCES['0'] == '\0'
        assert ESCAPE_SEQUENCES['"'] == '"'
        assert ESCAPE_SEQUENCES["'"] == "'"
        assert ESCAPE_SEQUENCES['\\'] == '\\'

    def test_parse_escape_sequence_newline(self):
        """Test parsing \\n escape."""
        result, pos = parse_escape_sequence('\\n', 0)
        assert result == '\n'
        assert pos == 2

    def test_parse_escape_sequence_tab(self):
        """Test parsing \\t escape."""
        result, pos = parse_escape_sequence('\\t', 0)
        assert result == '\t'
        assert pos == 2

    def test_parse_escape_sequence_quote(self):
        """Test parsing \\" escape."""
        result, pos = parse_escape_sequence('\\"', 0)
        assert result == '"'
        assert pos == 2

    def test_parse_escape_sequence_backslash(self):
        """Test parsing \\\\ escape."""
        result, pos = parse_escape_sequence('\\\\', 0)
        assert result == '\\'
        assert pos == 2

    def test_parse_escape_sequence_in_text(self):
        """Test parsing escape in middle of text."""
        text = 'hello\\nworld'
        result, pos = parse_escape_sequence(text, 5)
        assert result == '\n'
        assert pos == 7

    def test_parse_escape_sequence_invalid(self):
        """Test invalid escape sequence."""
        with pytest.raises(ValueError, match="Invalid escape sequence"):
            parse_escape_sequence('\\x', 0)

    def test_parse_escape_sequence_unterminated(self):
        """Test unterminated escape sequence."""
        with pytest.raises(ValueError, match="Unexpected end"):
            parse_escape_sequence('\\', 0)


class TestIsDigit:
    """Test is_digit helper function."""

    def test_digits(self):
        """Test that digits are recognized."""
        for d in '0123456789':
            assert is_digit(d)

    def test_non_digits(self):
        """Test that non-digits are not recognized."""
        assert not is_digit('a')
        assert not is_digit('Z')
        assert not is_digit('_')
        assert not is_digit(' ')
        assert not is_digit('')
        assert not is_digit('12')  # Multi-char


class TestIntegerLiterals:
    """Test integer literal parsing."""

    def test_single_digit(self):
        """Test single digit integer."""
        result, pos = parse_integer('5', 0)
        assert result == '5'
        assert pos == 1

    def test_multiple_digits(self):
        """Test multiple digit integer."""
        result, pos = parse_integer('123', 0)
        assert result == '123'
        assert pos == 3

    def test_large_number(self):
        """Test large integer."""
        result, pos = parse_integer('987654321', 0)
        assert result == '987654321'
        assert pos == 9

    def test_zero(self):
        """Test zero."""
        result, pos = parse_integer('0', 0)
        assert result == '0'
        assert pos == 1

    def test_long_suffix_uppercase(self):
        """Test integer with L suffix."""
        result, pos = parse_integer('123L', 0)
        assert result == '123L'
        assert pos == 4

    def test_long_suffix_lowercase(self):
        """Test integer with l suffix."""
        result, pos = parse_integer('456l', 0)
        assert result == '456l'
        assert pos == 4

    def test_integer_followed_by_text(self):
        """Test integer followed by non-digit."""
        result, pos = parse_integer('42abc', 0)
        assert result == '42'
        assert pos == 2

    def test_integer_at_position(self):
        """Test parsing integer at non-zero position."""
        result, pos = parse_integer('x = 42', 4)
        assert result == '42'
        assert pos == 6

    def test_not_integer(self):
        """Test when text doesn't start with integer."""
        result = parse_integer('abc', 0)
        assert result is None


class TestFloatLiterals:
    """Test float/double literal parsing."""

    def test_basic_float(self):
        """Test basic float with decimal point."""
        result, pos = parse_float('3.14', 0)
        assert result == '3.14'
        assert pos == 4

    def test_float_with_zero(self):
        """Test float starting with zero."""
        result, pos = parse_float('0.5', 0)
        assert result == '0.5'
        assert pos == 3

    def test_float_no_fraction(self):
        """Test float with no fractional part."""
        result, pos = parse_float('2.0', 0)
        assert result == '2.0'
        assert pos == 3

    def test_float_no_integer(self):
        """Test float with no integer part."""
        result, pos = parse_float('.5', 0)
        assert result == '.5'
        assert pos == 2

    def test_float_suffix_f_lowercase(self):
        """Test float with f suffix."""
        result, pos = parse_float('3.14f', 0)
        assert result == '3.14f'
        assert pos == 5

    def test_float_suffix_f_uppercase(self):
        """Test float with F suffix."""
        result, pos = parse_float('3.14F', 0)
        assert result == '3.14F'
        assert pos == 5

    def test_float_suffix_d_lowercase(self):
        """Test float with d suffix."""
        result, pos = parse_float('3.14d', 0)
        assert result == '3.14d'
        assert pos == 5

    def test_float_suffix_d_uppercase(self):
        """Test float with D suffix."""
        result, pos = parse_float('3.14D', 0)
        assert result == '3.14D'
        assert pos == 5

    def test_float_at_position(self):
        """Test parsing float at non-zero position."""
        result, pos = parse_float('x = 3.14', 4)
        assert result == '3.14'
        assert pos == 8

    def test_not_float_no_decimal(self):
        """Test integer without decimal is not float."""
        result = parse_float('123', 0)
        assert result is None

    def test_not_float_no_digits(self):
        """Test decimal point alone is not float."""
        result = parse_float('.', 0)
        assert result is None


class TestStringInterpolation:
    """Test string interpolation parsing."""

    def test_plain_string(self):
        """Test plain string without interpolation."""
        parts, pos = parse_string_interpolation('hello"', 0)
        assert len(parts) == 1
        assert parts[0] == ('STRING_PART', 'hello')
        assert pos == 6

    def test_empty_string(self):
        """Test empty string."""
        parts, pos = parse_string_interpolation('"', 0)
        assert len(parts) == 1
        assert parts[0] == ('STRING_PART', '')
        assert pos == 1

    def test_inline_interpolation(self):
        """Test inline variable interpolation."""
        parts, pos = parse_string_interpolation('Hello {name}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', 'Hello ')
        assert parts[1] == ('INTERP_VAR', 'name')
        assert parts[2] == ('STRING_PART', '')
        assert pos == 13

    def test_positional_interpolation(self):
        """Test positional interpolation."""
        parts, pos = parse_string_interpolation('User {@1}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', 'User ')
        assert parts[1] == ('INTERP_POS', '1')
        assert parts[2] == ('STRING_PART', '')
        assert pos == 10

    def test_multiple_interpolations(self):
        """Test multiple interpolations."""
        parts, pos = parse_string_interpolation('Hello {name}, you are {age} years old"', 0)
        assert len(parts) == 5
        assert parts[0] == ('STRING_PART', 'Hello ')
        assert parts[1] == ('INTERP_VAR', 'name')
        assert parts[2] == ('STRING_PART', ', you are ')
        assert parts[3] == ('INTERP_VAR', 'age')
        assert parts[4] == ('STRING_PART', ' years old')
        assert pos == 38

    def test_positional_multiple(self):
        """Test multiple positional interpolations."""
        parts, pos = parse_string_interpolation('User {@1} is {@2} years old"', 0)
        assert len(parts) == 5
        assert parts[0] == ('STRING_PART', 'User ')
        assert parts[1] == ('INTERP_POS', '1')
        assert parts[2] == ('STRING_PART', ' is ')
        assert parts[3] == ('INTERP_POS', '2')
        assert parts[4] == ('STRING_PART', ' years old')
        assert pos == 28

    def test_escape_sequences_in_string(self):
        """Test escape sequences in interpolated string."""
        parts, pos = parse_string_interpolation('Line 1\\nLine 2"', 0)
        assert len(parts) == 1
        assert parts[0] == ('STRING_PART', 'Line 1\nLine 2')
        assert pos == 15

    def test_escaped_quote_in_string(self):
        """Test escaped quote in string."""
        parts, pos = parse_string_interpolation('He said \\"Hello\\""', 0)
        assert len(parts) == 1
        assert parts[0] == ('STRING_PART', 'He said "Hello"')
        assert pos == 18

    def test_interpolation_at_start(self):
        """Test interpolation at start of string."""
        parts, pos = parse_string_interpolation('{name} says hello"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', '')
        assert parts[1] == ('INTERP_VAR', 'name')
        assert parts[2] == ('STRING_PART', ' says hello')
        assert pos == 18

    def test_interpolation_at_end(self):
        """Test interpolation at end of string."""
        parts, pos = parse_string_interpolation('Hello {name}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', 'Hello ')
        assert parts[1] == ('INTERP_VAR', 'name')
        assert parts[2] == ('STRING_PART', '')
        assert pos == 13

    def test_unterminated_string(self):
        """Test error on unterminated string."""
        with pytest.raises(ValueError, match="Unterminated string"):
            parse_string_interpolation('hello', 0)

    def test_unterminated_interpolation(self):
        """Test error on unterminated interpolation."""
        with pytest.raises(ValueError, match="Expected }"):
            parse_string_interpolation('hello {name"', 0)


class TestStringParsing:
    """Test complete string parsing with quotes."""

    def test_basic_string(self):
        """Test basic string parsing."""
        result, pos = parse_string('"hello"', 0)
        parts = json.loads(result)
        assert len(parts) == 1
        assert parts[0] == ['STRING_PART', 'hello']
        assert pos == 7

    def test_string_with_interpolation(self):
        """Test string with interpolation."""
        result, pos = parse_string('"Hello {name}"', 0)
        parts = json.loads(result)
        assert len(parts) == 3
        assert parts[0] == ['STRING_PART', 'Hello ']
        assert parts[1] == ['INTERP_VAR', 'name']
        assert pos == 14

    def test_not_string(self):
        """Test when text doesn't start with quote."""
        result = parse_string('hello', 0)
        assert result is None


class TestCharacterLiterals:
    """Test character literal parsing."""

    def test_basic_char(self):
        """Test basic character literal."""
        result, pos = parse_char("'a'", 0)
        assert result == "'a'"
        assert pos == 3

    def test_char_digit(self):
        """Test digit as character."""
        result, pos = parse_char("'5'", 0)
        assert result == "'5'"
        assert pos == 3

    def test_char_uppercase(self):
        """Test uppercase character."""
        result, pos = parse_char("'Z'", 0)
        assert result == "'Z'"
        assert pos == 3

    def test_char_space(self):
        """Test space as character."""
        result, pos = parse_char("' '", 0)
        assert result == "' '"
        assert pos == 3

    def test_char_escape_newline(self):
        """Test escaped newline in char."""
        result, pos = parse_char("'\\n'", 0)
        assert result == "'\\n'"
        assert pos == 4

    def test_char_escape_tab(self):
        """Test escaped tab in char."""
        result, pos = parse_char("'\\t'", 0)
        assert result == "'\\t'"
        assert pos == 4

    def test_char_escape_quote(self):
        """Test escaped single quote in char."""
        result, pos = parse_char("'\\''", 0)
        assert result == "'\\''"
        assert pos == 4

    def test_char_escape_backslash(self):
        """Test escaped backslash in char."""
        result, pos = parse_char("'\\\\'", 0)
        assert result == "'\\\\'"
        assert pos == 4

    def test_not_char(self):
        """Test when text doesn't start with single quote."""
        result = parse_char('"a"', 0)
        assert result is None

    def test_char_unterminated(self):
        """Test unterminated char literal."""
        with pytest.raises(ValueError, match="Unterminated character"):
            parse_char("'a", 0)


class TestHelperFunctions:
    """Test helper utility functions."""

    def test_is_literal_start_digit(self):
        """Test literal start with digit."""
        for d in '0123456789':
            assert is_literal_start(d)

    def test_is_literal_start_quote(self):
        """Test literal start with quote."""
        assert is_literal_start('"')
        assert is_literal_start("'")

    def test_is_literal_start_non_literal(self):
        """Test non-literal characters."""
        assert not is_literal_start('a')
        assert not is_literal_start('+')
        assert not is_literal_start(' ')

    def test_decode_string_parts(self):
        """Test decoding JSON string parts."""
        json_str = json.dumps([['STRING_PART', 'hello'], ['INTERP_VAR', 'name']])
        parts = decode_string_parts(json_str)
        assert len(parts) == 2
        assert parts[0] == ['STRING_PART', 'hello']
        assert parts[1] == ['INTERP_VAR', 'name']

    def test_has_interpolation_true(self):
        """Test detecting interpolation."""
        json_str = json.dumps([['STRING_PART', 'Hello '], ['INTERP_VAR', 'name']])
        assert has_interpolation(json_str)

    def test_has_interpolation_false(self):
        """Test string without interpolation."""
        json_str = json.dumps([['STRING_PART', 'hello']])
        assert not has_interpolation(json_str)

    def test_get_plain_string(self):
        """Test getting plain string value."""
        json_str = json.dumps([['STRING_PART', 'hello world']])
        result = get_plain_string(json_str)
        assert result == 'hello world'

    def test_get_plain_string_with_interpolation(self):
        """Test getting string with interpolation returns JSON."""
        json_str = json.dumps([['STRING_PART', 'Hello '], ['INTERP_VAR', 'name']])
        result = get_plain_string(json_str)
        assert result == json_str  # Returns JSON for interpolated strings


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_integer_zero_prefix(self):
        """Test integer with leading zeros."""
        result, pos = parse_integer('007', 0)
        assert result == '007'
        assert pos == 3

    def test_float_many_decimals(self):
        """Test float with many decimal places."""
        result, pos = parse_float('3.141592653589793', 0)
        assert result == '3.141592653589793'
        assert pos == 17

    def test_string_only_interpolation(self):
        """Test string with only interpolation, no plain text."""
        parts, pos = parse_string_interpolation('{name}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', '')
        assert parts[1] == ('INTERP_VAR', 'name')
        assert parts[2] == ('STRING_PART', '')

    def test_string_many_escapes(self):
        """Test string with multiple escape sequences."""
        parts, pos = parse_string_interpolation('\\n\\t\\r\\\\"', 0)
        assert len(parts) == 1
        assert parts[0] == ('STRING_PART', '\n\t\r\\')

    def test_interpolation_underscore_in_name(self):
        """Test interpolation with underscore in variable name."""
        parts, pos = parse_string_interpolation('{user_name}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', '')
        assert parts[1] == ('INTERP_VAR', 'user_name')
        assert parts[2] == ('STRING_PART', '')

    def test_interpolation_number_in_name(self):
        """Test interpolation with number in variable name."""
        parts, pos = parse_string_interpolation('{var1}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', '')
        assert parts[1] == ('INTERP_VAR', 'var1')
        assert parts[2] == ('STRING_PART', '')

    def test_positional_multiple_digits(self):
        """Test positional interpolation with multi-digit index."""
        parts, pos = parse_string_interpolation('{@123}"', 0)
        assert len(parts) == 3
        assert parts[0] == ('STRING_PART', '')
        assert parts[1] == ('INTERP_POS', '123')
        assert parts[2] == ('STRING_PART', '')
