"""Error handling and diagnostics for Fusion compiler.

This module provides error and warning reporting infrastructure for the lexer
and other compiler phases.
"""

import sys
from typing import Optional
from src.lexer.token import SourceLocation


class LexerError(Exception):
    """Lexer error with source location information.

    This exception is raised when the lexer encounters an error during
    tokenization, such as unterminated strings, invalid characters, etc.

    Attributes:
        message: Human-readable error message
        location: Source location where the error occurred
    """

    def __init__(self, message: str, location: SourceLocation):
        """Initialize lexer error.

        Args:
            message: Error message describing what went wrong
            location: Source location where the error occurred
        """
        self.message = message
        self.location = location
        # Format: "filename:line:col: error: message"
        super().__init__(f"{location}: error: {message}")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"LexerError('{self.message}', {self.location})"


class LexerWarning:
    """Lexer warning with source location information.

    Warnings are non-fatal issues that should be reported to the user
    but don't prevent compilation from continuing.

    Attributes:
        message: Human-readable warning message
        location: Source location where the warning occurred
    """

    def __init__(self, message: str, location: SourceLocation):
        """Initialize lexer warning.

        Args:
            message: Warning message describing the issue
            location: Source location where the warning occurred
        """
        self.message = message
        self.location = location

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"LexerWarning('{self.message}', {self.location})"

    def format(self) -> str:
        """Format warning for display.

        Returns:
            Formatted string like "filename:line:col: warning: message"
        """
        return f"{self.location}: warning: {self.message}"


class DiagnosticReporter:
    """Collects and reports errors and warnings.

    This class maintains lists of errors and warnings encountered during
    compilation and provides methods to display them.

    Attributes:
        errors: List of all errors encountered
        warnings: List of all warnings encountered
        error_count: Number of errors
        warning_count: Number of warnings
    """

    def __init__(self):
        """Initialize diagnostic reporter."""
        self.errors: list[LexerError] = []
        self.warnings: list[LexerWarning] = []

    @property
    def error_count(self) -> int:
        """Get number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Get number of warnings."""
        return len(self.warnings)

    def add_error(self, error: LexerError):
        """Add an error to the list.

        Args:
            error: LexerError to add
        """
        self.errors.append(error)

    def add_warning(self, warning: LexerWarning):
        """Add a warning to the list.

        Args:
            warning: LexerWarning to add
        """
        self.warnings.append(warning)

    def report_all(self, file=sys.stderr):
        """Print all errors and warnings to stderr.

        Args:
            file: Output file (default: stderr)
        """
        # Print warnings first
        for warning in self.warnings:
            print(warning.format(), file=file)

        # Then print errors
        for error in self.errors:
            print(str(error), file=file)

        # Print summary
        if self.error_count > 0 or self.warning_count > 0:
            summary = []
            if self.error_count > 0:
                summary.append(f"{self.error_count} error(s)")
            if self.warning_count > 0:
                summary.append(f"{self.warning_count} warning(s)")
            print(f"\n{', '.join(summary)} generated.", file=file)

    def has_errors(self) -> bool:
        """Check if any errors were reported.

        Returns:
            True if there are any errors, False otherwise
        """
        return self.error_count > 0

    def clear(self):
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()


# Pre-defined error messages for common lexer errors
class LexerErrorMessages:
    """Standard error messages for lexer errors."""

    @staticmethod
    def unterminated_string() -> str:
        """Error message for unterminated string literal."""
        return "Unterminated string literal"

    @staticmethod
    def unterminated_char() -> str:
        """Error message for unterminated character literal."""
        return "Unterminated character literal"

    @staticmethod
    def unterminated_comment() -> str:
        """Error message for unterminated multi-line comment."""
        return "Unterminated multi-line comment"

    @staticmethod
    def invalid_character(char: str) -> str:
        """Error message for invalid character.

        Args:
            char: The invalid character

        Returns:
            Error message with character code
        """
        code = ord(char)
        if char.isprintable():
            return f"Invalid character: '{char}' (U+{code:04X})"
        else:
            return f"Invalid character: U+{code:04X}"

    @staticmethod
    def invalid_escape_sequence(seq: str) -> str:
        """Error message for invalid escape sequence.

        Args:
            seq: The invalid escape sequence

        Returns:
            Error message
        """
        return f"Invalid escape sequence: '\\{seq}'"

    @staticmethod
    def mixed_tabs_spaces() -> str:
        """Warning message for mixed tabs and spaces in indentation."""
        return "Mixed tabs and spaces in indentation"

    @staticmethod
    def indentation_mismatch(expected: int, actual: int) -> str:
        """Error message for indentation mismatch.

        Args:
            expected: Expected indentation level
            actual: Actual indentation level

        Returns:
            Error message
        """
        return f"Indentation mismatch: expected {expected} spaces, got {actual}"

    @staticmethod
    def invalid_number_format(value: str) -> str:
        """Error message for invalid number format.

        Args:
            value: The invalid number string

        Returns:
            Error message
        """
        return f"Invalid number format: '{value}'"

    @staticmethod
    def unexpected_character_in_number(char: str) -> str:
        """Error message for unexpected character in number.

        Args:
            char: The unexpected character

        Returns:
            Error message
        """
        return f"Unexpected character in number: '{char}'"
