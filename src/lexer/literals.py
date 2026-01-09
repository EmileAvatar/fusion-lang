"""Literal tokenization for Fusion lexer.

This module provides literal value parsing including:
- Integer literals (decimal, with optional L/l suffix)
- Float/Double literals (with optional f/F/d/D suffix)
- String literals with interpolation support ({var} and {@1})
- Character literals with escape sequences
- Boolean literals (true/false - handled by keywords)
- Null literal (handled by keywords)
"""

from typing import Tuple, List, Optional, Union
import json
import re

from src.utils.errors import LexerError, LexerErrorMessages
from src.lexer.token import SourceLocation


# ============================================================
# Escape Sequence Support
# ============================================================

ESCAPE_SEQUENCES = {
    'n': '\n',   # Newline
    't': '\t',   # Tab
    'r': '\r',   # Carriage return
    '0': '\0',   # Null character
    '"': '"',    # Double quote
    "'": "'",    # Single quote
    '\\': '\\',  # Backslash
}


def parse_escape_sequence(text: str, position: int) -> Tuple[str, int]:
    """Parse an escape sequence starting at position.

    Args:
        text: The source text
        position: Current position (should be at backslash)

    Returns:
        Tuple of (escaped_char, new_position)

    Raises:
        ValueError: If escape sequence is invalid
    """
    if position >= len(text) or text[position] != '\\':
        raise ValueError(f"Expected backslash at position {position}")

    if position + 1 >= len(text):
        raise ValueError("Unexpected end of string in escape sequence")

    escape_char = text[position + 1]

    if escape_char in ESCAPE_SEQUENCES:
        return ESCAPE_SEQUENCES[escape_char], position + 2

    # Unknown escape sequence
    raise ValueError(f"Invalid escape sequence: \\{escape_char}")


# ============================================================
# Integer Literal Parsing
# ============================================================

def is_digit(char: str) -> bool:
    """Check if character is a digit."""
    return char and len(char) == 1 and '0' <= char <= '9'


def parse_integer(text: str, position: int) -> Optional[Tuple[str, int]]:
    """Parse an integer literal starting at position.

    Supports:
    - Decimal integers: 123, 456
    - Long suffix: 123L, 456l

    Args:
        text: The source text
        position: Current position

    Returns:
        Tuple of (integer_string, new_position) or None if not an integer
    """
    if position >= len(text) or not is_digit(text[position]):
        return None

    start = position
    pos = position

    # Read all digits
    while pos < len(text) and is_digit(text[pos]):
        pos += 1

    # Check for long suffix (L or l)
    if pos < len(text) and text[pos] in 'Ll':
        pos += 1

    return text[start:pos], pos


# ============================================================
# Float/Double Literal Parsing
# ============================================================

def parse_float(text: str, position: int) -> Optional[Tuple[str, int]]:
    """Parse a float/double literal starting at position.

    Supports:
    - Basic floats: 3.14, 0.5, 2.0
    - Float suffix: 3.14f, 3.14F
    - Double suffix: 3.14d, 3.14D
    - Scientific notation: 1e5, 2.5e-3 (future support)

    Args:
        text: The source text
        position: Current position

    Returns:
        Tuple of (float_string, new_position) or None if not a float

    Note:
        Requires at least one digit before or after decimal point.
    """
    if position >= len(text):
        return None

    start = position
    pos = position

    # Read integer part (optional if decimal point follows)
    has_integer_part = False
    while pos < len(text) and is_digit(text[pos]):
        has_integer_part = True
        pos += 1

    # Must have decimal point for float
    if pos >= len(text) or text[pos] != '.':
        return None

    pos += 1  # Skip decimal point

    # Read fractional part
    has_fractional_part = False
    while pos < len(text) and is_digit(text[pos]):
        has_fractional_part = True
        pos += 1

    # Must have at least one digit somewhere
    if not has_integer_part and not has_fractional_part:
        return None

    # Check for suffix (f, F, d, D)
    if pos < len(text) and text[pos] in 'fFdD':
        pos += 1

    return text[start:pos], pos


# ============================================================
# String Interpolation Support
# ============================================================

StringPart = Union[Tuple[str, str], Tuple[str, str, str]]  # ('STRING_PART', text) or ('INTERP_VAR', name) or ('INTERP_POS', index)


def parse_string_interpolation(text: str, position: int) -> Tuple[List[StringPart], int]:
    """Parse string contents with interpolation support.

    Supports:
    - Inline interpolation: {varName}
    - Positional interpolation: {@1}, {@2}
    - Escape sequences: \n, \t, \", \\, etc.

    Args:
        text: The source text
        position: Current position (should be after opening quote)

    Returns:
        Tuple of (parts_list, new_position)
        parts_list contains tuples: ('STRING_PART', text), ('INTERP_VAR', name), ('INTERP_POS', index)

    Raises:
        ValueError: If string is malformed
    """
    parts: List[StringPart] = []
    current_str = ""
    pos = position

    while pos < len(text) and text[pos] != '"':
        if text[pos] == '\\':
            # Escape sequence
            try:
                escaped_char, pos = parse_escape_sequence(text, pos)
                current_str += escaped_char
            except ValueError as e:
                raise ValueError(f"Invalid escape sequence at position {pos}: {e}")

        elif text[pos] == '{':
            # Interpolation start
            # Always add STRING_PART (even if empty) before interpolation
            parts.append(('STRING_PART', current_str))
            current_str = ""

            pos += 1  # Skip {

            if pos >= len(text):
                raise ValueError("Unexpected end of string in interpolation")

            if text[pos] == '@':
                # Positional interpolation: {@1}
                pos += 1  # Skip @

                # Read number
                num_start = pos
                while pos < len(text) and is_digit(text[pos]):
                    pos += 1

                if pos == num_start:
                    raise ValueError("Expected number after @ in positional interpolation")

                index = text[num_start:pos]
                parts.append(('INTERP_POS', index))

            else:
                # Inline interpolation: {varName}
                # Read identifier (alphanumeric + underscore)
                ident_start = pos
                while pos < len(text) and (text[pos].isalnum() or text[pos] == '_'):
                    pos += 1

                if pos == ident_start:
                    raise ValueError("Expected variable name in inline interpolation")

                var_name = text[ident_start:pos]
                parts.append(('INTERP_VAR', var_name))

            # Expect closing }
            if pos >= len(text) or text[pos] != '}':
                raise ValueError("Expected } to close interpolation")

            pos += 1  # Skip }

        else:
            # Regular character
            current_str += text[pos]
            pos += 1

    # Always add final string part (even if empty) after last interpolation or content
    parts.append(('STRING_PART', current_str))

    # Check for closing quote
    if pos >= len(text) or text[pos] != '"':
        raise ValueError("Unterminated string literal")

    pos += 1  # Skip closing "

    return parts, pos


def parse_string(text: str, position: int) -> Optional[Tuple[str, int]]:
    """Parse a string literal with interpolation support.

    Args:
        text: The source text
        position: Current position (should be at opening quote)

    Returns:
        Tuple of (json_encoded_parts, new_position) or None if not a string
        The json_encoded_parts is a JSON string containing the interpolation parts

    Raises:
        ValueError: If string is malformed
    """
    if position >= len(text) or text[position] != '"':
        return None

    pos = position + 1  # Skip opening "

    try:
        parts, pos = parse_string_interpolation(text, pos)
        # Return JSON-encoded parts for storage in token value
        return json.dumps(parts), pos
    except ValueError:
        # Re-raise with original position info
        raise


# ============================================================
# Character Literal Parsing
# ============================================================

def parse_char(text: str, position: int) -> Optional[Tuple[str, int]]:
    """Parse a character literal.

    Supports:
    - Basic chars: 'a', 'Z', '0'
    - Escape sequences: '\\n', '\\t', '\\\\'

    Args:
        text: The source text
        position: Current position (should be at opening single quote)

    Returns:
        Tuple of (char_string, new_position) or None if not a char

    Raises:
        ValueError: If char literal is malformed
    """
    if position >= len(text) or text[position] != "'":
        return None

    pos = position + 1  # Skip opening '
    start = position

    if pos >= len(text):
        raise ValueError("Unterminated character literal")

    # Check for escape sequence
    if text[pos] == '\\':
        try:
            _, pos = parse_escape_sequence(text, pos)
        except ValueError as e:
            raise ValueError(f"Invalid escape sequence in character literal: {e}")
    else:
        # Regular character
        pos += 1

    # Expect closing '
    if pos >= len(text) or text[pos] != "'":
        raise ValueError("Unterminated character literal (expected closing ')")

    pos += 1  # Skip closing '

    return text[start:pos], pos


# ============================================================
# Helper Functions
# ============================================================

def is_literal_start(char: str) -> bool:
    """Check if character can start a literal.

    Args:
        char: Single character to check

    Returns:
        True if char can start a literal
    """
    if not char or len(char) != 1:
        return False

    return is_digit(char) or char == '"' or char == "'"


def decode_string_parts(json_parts: str) -> List[StringPart]:
    """Decode JSON-encoded string parts back to list.

    Args:
        json_parts: JSON string from token value

    Returns:
        List of string parts as tuples
    """
    return json.loads(json_parts)


def has_interpolation(json_parts: str) -> bool:
    """Check if a string literal contains interpolation.

    Args:
        json_parts: JSON string from token value

    Returns:
        True if string contains interpolation
    """
    parts = json.loads(json_parts)
    return any(part[0] in ('INTERP_VAR', 'INTERP_POS') for part in parts)


def get_plain_string(json_parts: str) -> str:
    """Get plain string value without interpolation markers.

    Args:
        json_parts: JSON string from token value

    Returns:
        Plain string value (for non-interpolated strings)
    """
    parts = json.loads(json_parts)
    if len(parts) == 1 and parts[0][0] == 'STRING_PART':
        return parts[0][1]
    # Has interpolation - return JSON representation
    return json_parts
