"""Main lexer/tokenizer for Fusion programming language.

This module integrates all lexer components to produce a complete token stream
from Fusion source code.
"""

from typing import List, Optional
from .token import Token, TokenType, SourceLocation
from .indentation import IndentationTracker
from .block_style import BlockStyleTracker, BlockStyle
from .keywords import is_keyword, get_keyword_type
from .operators import match_operator, is_operator_char
from .literals import (
    parse_integer, parse_float, parse_string, parse_char,
    is_digit, is_literal_start
)
from .comments import is_comment_start, skip_comment
from src.utils.errors import LexerError, LexerWarning, DiagnosticReporter, LexerErrorMessages


class Lexer:
    """Main lexer class for tokenizing Fusion source code.

    The lexer maintains state for:
    - Current position in source text
    - Line and column tracking for error reporting
    - Indentation tracking for Python-style blocks
    - Block style tracking (braces/indent/End keywords)
    - Diagnostic collection (errors and warnings)

    Attributes:
        source: The source code to tokenize
        filename: Name of the source file (for error reporting)
        pos: Current position in source text
        line: Current line number (1-based)
        column: Current column number (1-based)
        indent_tracker: Tracks indentation levels
        block_tracker: Tracks block styles
        diagnostics: Collects errors and warnings
    """

    def __init__(self, source: str, filename: str = "<stdin>",
                 tab_width: int = 4, allow_mixed: bool = True):
        """Initialize the lexer.

        Args:
            source: Source code to tokenize
            filename: Name of source file (default: "<stdin>")
            tab_width: Spaces per tab for indentation tracking (default: 4). Normally left
                at the default and overridden via a project's fusion.toml [indentation]
                section instead of being passed directly - see src/config/project_config.py
                (Task 12.12).
            allow_mixed: Allow mixed tabs/spaces with a warning instead of an error
                (default: True). Same project-config note as tab_width.
        """
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1

        # Component trackers
        self.indent_tracker = IndentationTracker(tab_width=tab_width, allow_mixed=allow_mixed)
        self.block_tracker = BlockStyleTracker()
        self.diagnostics = DiagnosticReporter()

    # ============================================================
    # Position and Character Navigation
    # ============================================================

    def current_char(self) -> Optional[str]:
        """Get current character without advancing.

        Returns:
            Current character or None if at EOF
        """
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at character without advancing.

        Args:
            offset: Number of characters to look ahead (default: 1)

        Returns:
            Character at offset or None if beyond EOF
        """
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]

    def peek_string(self, length: int) -> str:
        """Peek ahead at a string of characters.

        Args:
            length: Number of characters to peek

        Returns:
            String of characters (may be shorter if EOF reached)
        """
        end_pos = min(self.pos + length, len(self.source))
        return self.source[self.pos:end_pos]

    def advance(self, count: int = 1) -> None:
        """Advance position by count characters.

        Args:
            count: Number of characters to advance (default: 1)
        """
        for _ in range(count):
            if self.pos < len(self.source):
                if self.source[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def is_eof(self) -> bool:
        """Check if at end of file.

        Returns:
            True if at EOF, False otherwise
        """
        return self.pos >= len(self.source)

    def location(self) -> SourceLocation:
        """Get current source location.

        Returns:
            SourceLocation for current position
        """
        return SourceLocation(self.filename, self.line, self.column)

    # ============================================================
    # Error Reporting
    # ============================================================

    def error(self, message: str) -> None:
        """Raise lexer error at current location.

        Args:
            message: Error message

        Raises:
            LexerError with current location
        """
        raise LexerError(message, self.location())

    def warning(self, warning: LexerWarning) -> None:
        """Add warning to diagnostics.

        Args:
            warning: LexerWarning to add
        """
        self.diagnostics.add_warning(warning)

    # ============================================================
    # Whitespace and Line Handling
    # ============================================================

    def skip_whitespace(self) -> None:
        """Skip horizontal whitespace (spaces and tabs).

        Does not skip newlines - those are handled separately.
        """
        while self.current_char() in [' ', '\t']:
            self.advance()

    def skip_line(self) -> None:
        """Skip to end of current line (but not the newline itself)."""
        while self.current_char() and self.current_char() != '\n':
            self.advance()

    def handle_newline(self) -> List[Token]:
        """Handle newline character and potential indentation changes.

        Returns:
            List of tokens (NEWLINE and potentially INDENT/DEDENT tokens)
        """
        tokens = []
        loc = self.location()

        # Emit NEWLINE token
        tokens.append(Token(TokenType.NEWLINE, '\n', loc))
        self.advance()  # Skip the \n

        return tokens

    def handle_indentation(self) -> List[Token]:
        """Process indentation at start of line.

        Returns:
            List of INDENT/DEDENT tokens (may be empty)
        """
        # Don't process indentation if inside brace blocks
        if self.block_tracker.is_inside_brace_block():
            return []

        # Get current line
        line = self.get_current_line()

        # Skip blank lines and comment-only lines
        if self.indent_tracker.should_skip_line(line):
            return []

        # Count indentation
        loc = self.location()
        indent_count, warning = self.indent_tracker.count_indentation(line, loc)

        # Add warning if any
        if warning:
            self.warning(warning)

        # Skip the leading whitespace we just counted
        # (count_indentation returns the number of equivalent spaces)
        whitespace_chars = 0
        while self.current_char() in [' ', '\t']:
            whitespace_chars += 1
            self.advance()

        # Process indentation change
        tokens = self.indent_tracker.process_indentation(indent_count, loc)

        # Update block tracker
        if tokens:
            for token in tokens:
                if token.type == TokenType.INDENT:
                    self.block_tracker.enter_indent_block()
                elif token.type == TokenType.DEDENT:
                    self.block_tracker.exit_indent_block()

        return tokens

    def get_current_line(self) -> str:
        """Get the current line from current position to end of line.

        Returns:
            String containing rest of current line (not including newline)
        """
        line_start = self.pos
        line_end = self.pos

        # Find end of line
        while line_end < len(self.source) and self.source[line_end] != '\n':
            line_end += 1

        return self.source[line_start:line_end]

    # ============================================================
    # Comment Handling
    # ============================================================

    def handle_comment(self) -> None:
        """Skip comment at current position.

        Raises:
            LexerError: If multi-line comment is unterminated
        """
        try:
            result = skip_comment(self.source, self.pos)
            if result:
                new_pos, lines = result
                # Update position
                for _ in range(lines):
                    self.line += 1
                    self.column = 1
                # Move to new position
                chars_advanced = new_pos - self.pos
                self.pos = new_pos
                # Update column if no newlines
                if lines == 0:
                    self.column += chars_advanced
        except ValueError as e:
            # Convert ValueError from skip_comment to LexerError
            self.error(LexerErrorMessages.unterminated_comment())

    # ============================================================
    # Identifier and Keyword Tokenization
    # ============================================================

    def tokenize_identifier_or_keyword(self) -> Token:
        """Tokenize identifier or keyword.

        Returns:
            Token (KEYWORD or IDENTIFIER)
        """
        loc = self.location()
        start = self.pos

        # Read alphanumeric and underscore characters
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()

        value = self.source[start:self.pos]

        # Check if it's a keyword
        if is_keyword(value):
            token_type = get_keyword_type(value)
            return Token(token_type, value, loc)

        # Otherwise it's an identifier
        return Token(TokenType.IDENTIFIER, value, loc)

    # ============================================================
    # Number Tokenization
    # ============================================================

    def tokenize_number(self) -> Token:
        """Tokenize integer or float literal.

        Returns:
            Token (INTEGER or FLOAT_LIT)

        Raises:
            LexerError: If number format is invalid
        """
        loc = self.location()

        # Try float first (includes decimal point)
        float_result = parse_float(self.source, self.pos)
        if float_result:
            value, new_pos = float_result
            self.pos = new_pos
            self.column += len(value)
            return Token(TokenType.FLOAT_LIT, value, loc)

        # Try integer
        int_result = parse_integer(self.source, self.pos)
        if int_result:
            value, new_pos = int_result
            self.pos = new_pos
            self.column += len(value)
            return Token(TokenType.INTEGER, value, loc)

        # Should not reach here if current_char is a digit
        self.error(LexerErrorMessages.invalid_number_format(self.current_char() or ""))

    # ============================================================
    # String Tokenization
    # ============================================================

    def tokenize_string(self) -> Token:
        """Tokenize string literal with interpolation support.

        Returns:
            Token (STRING_LIT)

        Raises:
            LexerError: If string is malformed or unterminated
        """
        loc = self.location()

        try:
            json_parts, new_pos = parse_string(self.source, self.pos)
            # Update position
            chars_advanced = new_pos - self.pos
            self.pos = new_pos
            self.column += chars_advanced

            return Token(TokenType.STRING_LIT, json_parts, loc)
        except ValueError as e:
            # Convert ValueError to LexerError
            if "Unterminated" in str(e):
                self.error(LexerErrorMessages.unterminated_string())
            else:
                self.error(str(e))

    # ============================================================
    # Character Literal Tokenization
    # ============================================================

    def tokenize_char(self) -> Token:
        """Tokenize character literal.

        Returns:
            Token (CHAR_LIT)

        Raises:
            LexerError: If char literal is malformed or unterminated
        """
        loc = self.location()

        try:
            value, new_pos = parse_char(self.source, self.pos)
            # Update position
            chars_advanced = new_pos - self.pos
            self.pos = new_pos
            self.column += chars_advanced

            return Token(TokenType.CHAR_LIT, value, loc)
        except ValueError as e:
            # Convert ValueError to LexerError
            if "Unterminated" in str(e):
                self.error(LexerErrorMessages.unterminated_char())
            else:
                self.error(str(e))

    # ============================================================
    # Operator and Delimiter Tokenization
    # ============================================================

    def tokenize_operator(self) -> Token:
        """Tokenize operator or delimiter.

        Returns:
            Token (operator or delimiter type)

        Raises:
            LexerError: If character is not a valid operator/delimiter
        """
        loc = self.location()

        # Try to match operator
        result = match_operator(self.source, self.pos)
        if result:
            token_type, value, new_pos = result
            # Update position
            chars_advanced = new_pos - self.pos
            self.pos = new_pos
            self.column += chars_advanced

            # Track brace blocks
            if token_type == TokenType.LBRACE:
                self.block_tracker.enter_brace_block()
            elif token_type == TokenType.RBRACE:
                try:
                    self.block_tracker.exit_brace_block()
                except Exception as e:
                    self.error(str(e))

            return Token(token_type, value, loc)

        # Invalid character
        ch = self.current_char()
        if ch:
            self.error(LexerErrorMessages.invalid_character(ch))
        else:
            self.error("Unexpected end of file")

    # ============================================================
    # Main Tokenization Loop
    # ============================================================

    def tokenize(self) -> List[Token]:
        """Tokenize entire source code.

        Returns:
            List of tokens including EOF token

        Raises:
            LexerError: On any lexical error
        """
        tokens = []

        while not self.is_eof():
            ch = self.current_char()

            # End of file
            if ch is None:
                break

            # Newline - handle it and process indentation on next line
            if ch == '\n':
                newline_tokens = self.handle_newline()
                tokens.extend(newline_tokens)
                # After newline, handle indentation at start of next line
                # (handle_indentation will consume the whitespace itself)
                if not self.is_eof():
                    indent_tokens = self.handle_indentation()
                    tokens.extend(indent_tokens)
                continue

            # Whitespace (spaces/tabs) - skip
            if ch in [' ', '\t']:
                self.skip_whitespace()
                continue

            # Comments
            if is_comment_start(self.source, self.pos):
                self.handle_comment()
                continue

            # String literals
            if ch == '"':
                tokens.append(self.tokenize_string())
                continue

            # Character literals
            if ch == "'":
                tokens.append(self.tokenize_char())
                continue

            # Numbers
            if ch and ch.isdigit():
                tokens.append(self.tokenize_number())
                continue

            # Identifiers and keywords
            if ch and (ch.isalpha() or ch == '_'):
                tokens.append(self.tokenize_identifier_or_keyword())
                continue

            # Operators and delimiters
            if ch and is_operator_char(ch):
                tokens.append(self.tokenize_operator())
                continue

            # Invalid character
            self.error(LexerErrorMessages.invalid_character(ch))

        # Handle end of file
        loc = self.location()

        # Emit final DEDENTs
        final_dedents = self.indent_tracker.finalize(loc)
        tokens.extend(final_dedents)

        # Emit EOF token
        tokens.append(Token(TokenType.EOF, "", loc))

        return tokens


def lex(source: str, filename: str = "<stdin>") -> List[Token]:
    """Convenience function to tokenize source code.

    Args:
        source: Source code to tokenize
        filename: Name of source file (default: "<stdin>")

    Returns:
        List of tokens

    Raises:
        LexerError: On any lexical error
    """
    lexer = Lexer(source, filename)
    return lexer.tokenize()
