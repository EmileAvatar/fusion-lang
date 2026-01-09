"""Indentation tracking system for Python-style indentation-based blocks.

This module implements the INDENT/DEDENT token generation algorithm as specified
in the Fusion EBNF grammar. It maintains a stack of indentation levels and emits
appropriate tokens when indentation changes.
"""

from typing import List, Optional, Tuple
from .token import Token, TokenType, SourceLocation
from src.utils.errors import LexerError, LexerWarning, LexerErrorMessages


class IndentationTracker:
    """Tracks indentation levels and generates INDENT/DEDENT tokens.

    This class implements a stack-based algorithm for tracking indentation levels
    in Python-style indentation-based code blocks. It handles:
    - INDENT token emission when indentation increases
    - DEDENT token emission when indentation decreases (potentially multiple)
    - Validation of dedent alignment
    - Detection of mixed tabs/spaces
    - EOF dedent emission

    Attributes:
        indent_stack: Stack of indentation levels (starts with [0])
        tab_width: Number of spaces equivalent to one tab character
        allow_mixed: Whether to allow mixed tabs/spaces (warning vs error)
    """

    def __init__(self, tab_width: int = 4, allow_mixed: bool = True):
        """Initialize the indentation tracker.

        Args:
            tab_width: Number of spaces per tab character (default: 4)
            allow_mixed: Allow mixed tabs/spaces with warning (default: True)
        """
        self.indent_stack: List[int] = [0]  # Start with zero indentation
        self.tab_width: int = tab_width
        self.allow_mixed: bool = allow_mixed

    def current_level(self) -> int:
        """Get the current indentation level.

        Returns:
            The current indentation level in spaces
        """
        return self.indent_stack[-1]

    def reset(self) -> None:
        """Reset the indentation tracker to initial state."""
        self.indent_stack = [0]

    def count_indentation(
        self,
        line: str,
        location: SourceLocation
    ) -> Tuple[int, Optional[LexerWarning]]:
        """Count leading whitespace on a line.

        Args:
            line: The line to measure (should be at start of line)
            location: Source location for warnings/errors

        Returns:
            Tuple of (indentation_count, warning)
            warning is None if no issues detected, LexerWarning otherwise

        Raises:
            LexerError: If mixed tabs/spaces and allow_mixed is False
        """
        count = 0
        has_spaces = False
        has_tabs = False
        index = 0

        while index < len(line) and line[index] in [' ', '\t']:
            if line[index] == ' ':
                count += 1
                has_spaces = True
            elif line[index] == '\t':
                count += self.tab_width
                has_tabs = True
            index += 1

        # Check for mixed tabs/spaces
        warning = None
        if has_spaces and has_tabs:
            msg = LexerErrorMessages.mixed_tabs_spaces()
            if not self.allow_mixed:
                raise LexerError(msg, location)
            warning = LexerWarning(msg, location)

        return count, warning

    def process_indentation(
        self,
        indent_level: int,
        location: SourceLocation
    ) -> List[Token]:
        """Process indentation change and generate appropriate tokens.

        This is the core algorithm that compares the new indentation level
        with the current level and generates INDENT or DEDENT tokens.

        Args:
            indent_level: The new indentation level in spaces
            location: Source location for generated tokens

        Returns:
            List of Token objects (INDENT or DEDENT tokens, possibly empty)

        Raises:
            LexerError: If dedent doesn't align with previous level
        """
        tokens: List[Token] = []
        current = self.indent_stack[-1]

        if indent_level > current:
            # Indentation increase: push new level and emit INDENT
            self.indent_stack.append(indent_level)
            tokens.append(Token(TokenType.INDENT, "", location))

        elif indent_level < current:
            # Indentation decrease: pop levels and emit DEDENTs
            while len(self.indent_stack) > 0 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, "", location))

            # Validate that dedent aligns with a previous indentation level
            if self.indent_stack[-1] != indent_level:
                msg = LexerErrorMessages.indentation_mismatch(
                    self.indent_stack[-1], indent_level
                )
                raise LexerError(msg, location)

        # Equal indentation: no tokens emitted

        return tokens

    def finalize(self, location: SourceLocation) -> List[Token]:
        """Emit remaining DEDENT tokens at end of file.

        When EOF is reached, all open indentation blocks must be closed.
        This generates DEDENT tokens for each remaining level on the stack.

        Args:
            location: Source location for generated tokens

        Returns:
            List of DEDENT tokens (one per remaining indentation level)
        """
        tokens: List[Token] = []

        # Emit DEDENT for each level above 0
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "", location))

        return tokens

    def is_blank_line(self, line: str) -> bool:
        """Check if a line is blank (only whitespace).

        Args:
            line: The line to check

        Returns:
            True if line contains only whitespace or is empty
        """
        return len(line.strip()) == 0

    def is_comment_line(self, line: str) -> bool:
        """Check if a line contains only a comment (no code).

        Handles all three Fusion comment styles:
        - // single-line comment
        - ' single-line comment
        - /* multi-line comment (if starts on this line)

        Args:
            line: The line to check (leading whitespace stripped)

        Returns:
            True if line is comment-only
        """
        stripped = line.strip()

        if len(stripped) == 0:
            return False

        # Check for single-line comments
        if stripped.startswith('//') or stripped.startswith("'"):
            return True

        # Check for multi-line comment start
        if stripped.startswith('/*'):
            return True

        return False

    def should_skip_line(self, line: str) -> bool:
        """Check if a line should be skipped for indentation tracking.

        Lines that should be skipped:
        - Blank lines (only whitespace)
        - Comment-only lines

        Args:
            line: The line to check

        Returns:
            True if line should be skipped
        """
        return self.is_blank_line(line) or self.is_comment_line(line)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"IndentationTracker(stack={self.indent_stack}, current={self.current_level()})"
