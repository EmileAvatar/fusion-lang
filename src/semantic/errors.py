"""Semantic analysis error classes."""

from typing import Optional
from src.lexer.token import SourceLocation


class SemanticError(Exception):
    """Raised when semantic analysis fails.

    Attributes:
        message: Error message describing the semantic error
        location: Optional source location where the error occurred
    """

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        """Initialize a semantic error.

        Args:
            message: Error message
            location: Source location where error occurred (optional)
        """
        self.message = message
        self.location = location
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with location if available.

        Returns:
            Formatted error message string
        """
        if self.location:
            return f"{self.location}: {self.message}"
        return self.message

    def __repr__(self) -> str:
        """Return repr string."""
        return f"SemanticError({self.message!r}, {self.location!r})"
