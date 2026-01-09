"""Comment handling for Fusion lexer.

This module provides comment detection and skipping functionality for two
comment styles currently supported by Fusion:
1. // - C-style single-line comments
2. /* */ - C-style multi-line comments

NOTE: ' (single quote) comment support is DISABLED for now to allow
character literals 'c' syntax. Future: Enable ' only at line start.

Comments are not emitted as tokens; they are skipped during lexing.
"""

from typing import Optional, Tuple

from src.utils.errors import LexerError, LexerErrorMessages
from src.lexer.token import SourceLocation


def is_comment_start(text: str, position: int) -> bool:
    """Check if position starts a comment.

    Args:
        text: The source text
        position: Current position

    Returns:
        True if position starts any comment type

    Examples:
        >>> is_comment_start('// comment', 0)
        True
        >>> is_comment_start('/* comment */', 0)
        True
        >>> is_comment_start('int x', 0)
        False
    """
    if position >= len(text):
        return False

    # Check for // or /*
    if position + 1 < len(text):
        two_char = text[position:position + 2]
        if two_char == '//' or two_char == '/*':
            return True

    # NOTE: ' (single quote) is NOT checked here - disabled for now
    # to allow character literals like 'c'

    return False


def skip_single_line_comment(text: str, position: int) -> Tuple[int, int]:
    """Skip a single-line comment (//).

    Consumes characters until newline or end of file.

    Args:
        text: The source text
        position: Current position (should be at //)

    Returns:
        Tuple of (new_position, lines_consumed)
        new_position points to the newline or EOF
        lines_consumed is always 0 (single-line comments don't cross lines)

    Examples:
        >>> skip_single_line_comment('// comment\\ncode', 0)
        (10, 0)
    """
    pos = position

    # Skip //
    if pos + 1 < len(text) and text[pos:pos + 2] == '//':
        pos += 2
    else:
        # Not a single-line comment
        return position, 0

    # Consume until newline or EOF
    while pos < len(text) and text[pos] != '\n':
        pos += 1

    return pos, 0


def skip_multi_line_comment(text: str, position: int) -> Tuple[int, int]:
    """Skip a multi-line comment (/* */).

    Consumes characters until closing */ or EOF (error).

    Args:
        text: The source text
        position: Current position (should be at /*)

    Returns:
        Tuple of (new_position, lines_consumed)
        new_position points after the closing */
        lines_consumed is the number of newlines encountered

    Raises:
        ValueError: If comment is unterminated (reaches EOF before */)

    Examples:
        >>> skip_multi_line_comment('/* comment */code', 0)
        (13, 0)
        >>> skip_multi_line_comment('/* line1\\nline2 */code', 0)
        (17, 1)
    """
    pos = position

    # Must start with /*
    if pos + 1 >= len(text) or text[pos:pos + 2] != '/*':
        return position, 0

    pos += 2  # Skip /*
    lines = 0

    # Find closing */
    while pos < len(text):
        if text[pos] == '\n':
            lines += 1
            pos += 1
        elif pos + 1 < len(text) and text[pos:pos + 2] == '*/':
            pos += 2  # Skip */
            return pos, lines
        else:
            pos += 1

    # Reached EOF without finding */
    raise ValueError("Unterminated multi-line comment (missing */)")


def skip_comment(text: str, position: int) -> Optional[Tuple[int, int]]:
    """Skip any type of comment.

    This is the main entry point for comment handling. Detects comment type
    and delegates to appropriate handler.

    Args:
        text: The source text
        position: Current position

    Returns:
        Tuple of (new_position, lines_consumed) if comment found, None otherwise

    Raises:
        ValueError: If multi-line comment is unterminated

    Examples:
        >>> skip_comment('// comment\\n', 0)
        (10, 0)
        >>> skip_comment('/* comment */', 0)
        (13, 0)
        >>> skip_comment('int x', 0)
        None
    """
    if position >= len(text):
        return None

    # Check for multi-line comment first (to distinguish /* from //)
    if position + 1 < len(text) and text[position:position + 2] == '/*':
        return skip_multi_line_comment(text, position)

    # Check for single-line comments
    if position + 1 < len(text) and text[position:position + 2] == '//':
        return skip_single_line_comment(text, position)

    # NOTE: ' is NOT handled - disabled for char literal support

    return None


def get_comment_type(text: str, position: int) -> Optional[str]:
    """Get the type of comment at position.

    Args:
        text: The source text
        position: Current position

    Returns:
        'single' for //, 'multi' for /* */, None if not a comment

    Examples:
        >>> get_comment_type('// comment', 0)
        'single'
        >>> get_comment_type('/* comment */', 0)
        'multi'
        >>> get_comment_type('int x', 0)
        None
    """
    if position >= len(text):
        return None

    if position + 1 < len(text):
        two_char = text[position:position + 2]
        if two_char == '/*':
            return 'multi'
        if two_char == '//':
            return 'single'

    # NOTE: ' is NOT handled - disabled for char literal support

    return None
