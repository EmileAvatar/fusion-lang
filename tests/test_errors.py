"""Tests for error handling and diagnostics in Fusion lexer.

This module tests:
- LexerError exception with source location
- LexerWarning with source location
- DiagnosticReporter for collecting errors/warnings
- Error message formatting
"""

import pytest
import sys
from io import StringIO

from src.utils.errors import (
    LexerError,
    LexerWarning,
    DiagnosticReporter,
    LexerErrorMessages,
)
from src.lexer.token import SourceLocation


# ============================================================
# Tests: LexerError
# ============================================================


def test_lexer_error_creation():
    """Test creating a LexerError."""
    loc = SourceLocation("test.fusion", 10, 5)
    error = LexerError("Invalid character", loc)

    assert error.message == "Invalid character"
    assert error.location == loc
    assert error.location.line == 10
    assert error.location.column == 5


def test_lexer_error_string_format():
    """Test LexerError string formatting."""
    loc = SourceLocation("test.fusion", 10, 5)
    error = LexerError("Invalid character", loc)

    error_str = str(error)
    assert "test.fusion:10:5" in error_str
    assert "error:" in error_str
    assert "Invalid character" in error_str


def test_lexer_error_repr():
    """Test LexerError repr."""
    loc = SourceLocation("test.fusion", 10, 5)
    error = LexerError("Invalid character", loc)

    repr_str = repr(error)
    assert "LexerError" in repr_str
    assert "Invalid character" in repr_str


def test_lexer_error_is_exception():
    """Test that LexerError is an Exception."""
    loc = SourceLocation("test.fusion", 1, 1)
    error = LexerError("Test", loc)

    assert isinstance(error, Exception)


def test_lexer_error_can_be_raised():
    """Test that LexerError can be raised and caught."""
    loc = SourceLocation("test.fusion", 1, 1)

    with pytest.raises(LexerError) as exc_info:
        raise LexerError("Test error", loc)

    assert exc_info.value.message == "Test error"
    assert exc_info.value.location == loc


# ============================================================
# Tests: LexerWarning
# ============================================================


def test_lexer_warning_creation():
    """Test creating a LexerWarning."""
    loc = SourceLocation("test.fusion", 5, 10)
    warning = LexerWarning("Mixed tabs and spaces", loc)

    assert warning.message == "Mixed tabs and spaces"
    assert warning.location == loc
    assert warning.location.line == 5
    assert warning.location.column == 10


def test_lexer_warning_format():
    """Test LexerWarning formatting."""
    loc = SourceLocation("test.fusion", 5, 10)
    warning = LexerWarning("Mixed tabs and spaces", loc)

    formatted = warning.format()
    assert "test.fusion:5:10" in formatted
    assert "warning:" in formatted
    assert "Mixed tabs and spaces" in formatted


def test_lexer_warning_repr():
    """Test LexerWarning repr."""
    loc = SourceLocation("test.fusion", 5, 10)
    warning = LexerWarning("Mixed tabs and spaces", loc)

    repr_str = repr(warning)
    assert "LexerWarning" in repr_str
    assert "Mixed tabs and spaces" in repr_str


# ============================================================
# Tests: DiagnosticReporter
# ============================================================


def test_diagnostic_reporter_creation():
    """Test creating a DiagnosticReporter."""
    reporter = DiagnosticReporter()

    assert reporter.error_count == 0
    assert reporter.warning_count == 0
    assert not reporter.has_errors()


def test_diagnostic_reporter_add_error():
    """Test adding errors to reporter."""
    reporter = DiagnosticReporter()
    loc = SourceLocation("test.fusion", 1, 1)

    error1 = LexerError("Error 1", loc)
    error2 = LexerError("Error 2", loc)

    reporter.add_error(error1)
    assert reporter.error_count == 1
    assert reporter.has_errors()

    reporter.add_error(error2)
    assert reporter.error_count == 2


def test_diagnostic_reporter_add_warning():
    """Test adding warnings to reporter."""
    reporter = DiagnosticReporter()
    loc = SourceLocation("test.fusion", 1, 1)

    warning1 = LexerWarning("Warning 1", loc)
    warning2 = LexerWarning("Warning 2", loc)

    reporter.add_warning(warning1)
    assert reporter.warning_count == 1
    assert not reporter.has_errors()  # Warnings don't count as errors

    reporter.add_warning(warning2)
    assert reporter.warning_count == 2


def test_diagnostic_reporter_clear():
    """Test clearing all diagnostics."""
    reporter = DiagnosticReporter()
    loc = SourceLocation("test.fusion", 1, 1)

    reporter.add_error(LexerError("Error", loc))
    reporter.add_warning(LexerWarning("Warning", loc))

    assert reporter.error_count == 1
    assert reporter.warning_count == 1

    reporter.clear()

    assert reporter.error_count == 0
    assert reporter.warning_count == 0
    assert not reporter.has_errors()


def test_diagnostic_reporter_report_all():
    """Test reporting all diagnostics to stderr."""
    reporter = DiagnosticReporter()
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 5, 10)

    reporter.add_warning(LexerWarning("Mixed tabs", loc1))
    reporter.add_error(LexerError("Invalid char", loc2))

    # Capture stderr
    captured_output = StringIO()
    reporter.report_all(file=captured_output)

    output = captured_output.getvalue()

    # Check that warning appears first
    assert "warning:" in output
    assert "Mixed tabs" in output

    # Check that error appears
    assert "error:" in output
    assert "Invalid char" in output

    # Check summary
    assert "1 error(s)" in output
    assert "1 warning(s)" in output


def test_diagnostic_reporter_report_only_errors():
    """Test reporting when only errors exist."""
    reporter = DiagnosticReporter()
    loc = SourceLocation("test.fusion", 1, 1)

    reporter.add_error(LexerError("Error 1", loc))
    reporter.add_error(LexerError("Error 2", loc))

    captured_output = StringIO()
    reporter.report_all(file=captured_output)

    output = captured_output.getvalue()

    assert "error:" in output
    assert "2 error(s)" in output
    assert "warning" not in output or "0 warning" in output


def test_diagnostic_reporter_report_only_warnings():
    """Test reporting when only warnings exist."""
    reporter = DiagnosticReporter()
    loc = SourceLocation("test.fusion", 1, 1)

    reporter.add_warning(LexerWarning("Warning 1", loc))

    captured_output = StringIO()
    reporter.report_all(file=captured_output)

    output = captured_output.getvalue()

    assert "warning:" in output
    assert "1 warning(s)" in output


def test_diagnostic_reporter_no_output_when_empty():
    """Test that reporter produces no output when empty."""
    reporter = DiagnosticReporter()

    captured_output = StringIO()
    reporter.report_all(file=captured_output)

    output = captured_output.getvalue()
    assert output == ""


# ============================================================
# Tests: LexerErrorMessages
# ============================================================


def test_error_message_unterminated_string():
    """Test unterminated string error message."""
    msg = LexerErrorMessages.unterminated_string()
    assert "Unterminated string" in msg
    assert "literal" in msg.lower()


def test_error_message_unterminated_char():
    """Test unterminated char error message."""
    msg = LexerErrorMessages.unterminated_char()
    assert "Unterminated character" in msg
    assert "literal" in msg.lower()


def test_error_message_unterminated_comment():
    """Test unterminated comment error message."""
    msg = LexerErrorMessages.unterminated_comment()
    assert "Unterminated" in msg
    assert "comment" in msg.lower()


def test_error_message_invalid_character_printable():
    """Test invalid character message for printable char."""
    msg = LexerErrorMessages.invalid_character('@')
    assert "Invalid character" in msg
    assert "'@'" in msg
    assert "U+" in msg  # Unicode code point


def test_error_message_invalid_character_non_printable():
    """Test invalid character message for non-printable char."""
    msg = LexerErrorMessages.invalid_character('\x00')
    assert "Invalid character" in msg
    assert "U+0000" in msg
    assert "'" not in msg  # Non-printable chars shouldn't be quoted


def test_error_message_invalid_escape_sequence():
    """Test invalid escape sequence message."""
    msg = LexerErrorMessages.invalid_escape_sequence('x')
    assert "Invalid escape sequence" in msg
    assert "\\x" in msg


def test_error_message_mixed_tabs_spaces():
    """Test mixed tabs/spaces warning message."""
    msg = LexerErrorMessages.mixed_tabs_spaces()
    assert "Mixed tabs and spaces" in msg
    assert "indentation" in msg.lower()


def test_error_message_indentation_mismatch():
    """Test indentation mismatch error message."""
    msg = LexerErrorMessages.indentation_mismatch(4, 6)
    assert "Indentation mismatch" in msg
    assert "4" in msg
    assert "6" in msg


def test_error_message_invalid_number_format():
    """Test invalid number format error message."""
    msg = LexerErrorMessages.invalid_number_format("123abc")
    assert "Invalid number format" in msg
    assert "123abc" in msg


def test_error_message_unexpected_character_in_number():
    """Test unexpected character in number error message."""
    msg = LexerErrorMessages.unexpected_character_in_number('x')
    assert "Unexpected character" in msg
    assert "number" in msg.lower()
    assert "'x'" in msg


# ============================================================
# Integration Tests
# ============================================================


def test_multiple_errors_and_warnings():
    """Test collecting multiple errors and warnings."""
    reporter = DiagnosticReporter()

    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 5, 3)
    loc3 = SourceLocation("test.fusion", 10, 7)

    reporter.add_warning(LexerWarning("Warning 1", loc1))
    reporter.add_error(LexerError("Error 1", loc2))
    reporter.add_warning(LexerWarning("Warning 2", loc2))
    reporter.add_error(LexerError("Error 2", loc3))

    assert reporter.error_count == 2
    assert reporter.warning_count == 2
    assert reporter.has_errors()


def test_error_with_standard_message():
    """Test creating error with standard message."""
    loc = SourceLocation("test.fusion", 1, 1)
    msg = LexerErrorMessages.unterminated_string()
    error = LexerError(msg, loc)

    assert "Unterminated string" in str(error)
    assert "test.fusion:1:1" in str(error)


def test_warning_with_standard_message():
    """Test creating warning with standard message."""
    loc = SourceLocation("test.fusion", 5, 1)
    msg = LexerErrorMessages.mixed_tabs_spaces()
    warning = LexerWarning(msg, loc)

    assert "Mixed tabs and spaces" in warning.format()
    assert "test.fusion:5:1" in warning.format()
