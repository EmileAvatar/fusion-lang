"""Unit tests for IndentationTracker class.

Tests the indentation tracking system that generates INDENT/DEDENT tokens
for Python-style indentation-based blocks.
"""

import pytest
from src.lexer.indentation import IndentationTracker
from src.lexer.token import Token, TokenType, SourceLocation
from src.utils.errors import LexerError, LexerWarning


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def tracker():
    """Create a fresh IndentationTracker for each test."""
    return IndentationTracker(tab_width=4, allow_mixed=True)


@pytest.fixture
def location():
    """Create a test source location."""
    return SourceLocation("test.fusion", 1, 1)


# ============================================================
# Initialization Tests
# ============================================================

def test_initialization(tracker):
    """Test IndentationTracker initialization."""
    assert tracker.indent_stack == [0]
    assert tracker.current_level() == 0
    assert tracker.tab_width == 4
    assert tracker.allow_mixed is True


def test_reset(tracker, location):
    """Test reset method."""
    # Add some indentation
    tracker.process_indentation(4, location)
    assert tracker.current_level() == 4

    # Reset should go back to initial state
    tracker.reset()
    assert tracker.indent_stack == [0]
    assert tracker.current_level() == 0


# ============================================================
# Indentation Counting Tests
# ============================================================

def test_count_spaces(tracker, location):
    """Test counting space-only indentation."""
    count, warning = tracker.count_indentation("    code", location)
    assert count == 4
    assert warning is None


def test_count_tabs(tracker, location):
    """Test counting tab-only indentation."""
    count, warning = tracker.count_indentation("\tcode", location)
    assert count == 4  # 1 tab = 4 spaces
    assert warning is None


def test_count_multiple_tabs(tracker, location):
    """Test counting multiple tabs."""
    count, warning = tracker.count_indentation("\t\tcode", location)
    assert count == 8  # 2 tabs = 8 spaces
    assert warning is None


def test_count_no_indentation(tracker, location):
    """Test counting line with no indentation."""
    count, warning = tracker.count_indentation("code", location)
    assert count == 0
    assert warning is None


def test_count_mixed_tabs_spaces_warning(tracker, location):
    """Test warning on mixed tabs and spaces."""
    count, warning = tracker.count_indentation("\t  code", location)
    assert count == 6  # 1 tab (4) + 2 spaces
    assert warning is not None
    assert isinstance(warning, LexerWarning)
    assert "Mixed tabs and spaces" in warning.message


def test_count_mixed_tabs_spaces_error():
    """Test error on mixed tabs/spaces when not allowed."""
    tracker = IndentationTracker(tab_width=4, allow_mixed=False)
    location = SourceLocation("test.fusion", 1, 1)

    with pytest.raises(LexerError) as exc_info:
        tracker.count_indentation("\t  code", location)

    assert "Mixed tabs and spaces" in str(exc_info.value)


# ============================================================
# INDENT Token Generation Tests
# ============================================================

def test_simple_indent(tracker, location):
    """Test single level indentation increase."""
    tokens = tracker.process_indentation(4, location)

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.INDENT
    assert tracker.current_level() == 4


def test_multiple_indent_levels(tracker):
    """Test nested indentation."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)

    # First indent to 4
    tokens1 = tracker.process_indentation(4, loc1)
    assert len(tokens1) == 1
    assert tokens1[0].type == TokenType.INDENT
    assert tracker.current_level() == 4

    # Second indent to 8
    tokens2 = tracker.process_indentation(8, loc2)
    assert len(tokens2) == 1
    assert tokens2[0].type == TokenType.INDENT
    assert tracker.current_level() == 8


def test_no_change_in_indentation(tracker, location):
    """Test no tokens when indentation stays same."""
    # Indent to 4
    tracker.process_indentation(4, location)

    # Stay at 4
    tokens = tracker.process_indentation(4, location)
    assert len(tokens) == 0
    assert tracker.current_level() == 4


# ============================================================
# DEDENT Token Generation Tests
# ============================================================

def test_simple_dedent(tracker):
    """Test single level dedent."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)

    # Indent to 4
    tracker.process_indentation(4, loc1)

    # Dedent back to 0
    tokens = tracker.process_indentation(0, loc2)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.DEDENT
    assert tracker.current_level() == 0


def test_multiple_dedents(tracker):
    """Test multiple dedents at once."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)
    loc3 = SourceLocation("test.fusion", 3, 1)

    # Indent to 4, then 8
    tracker.process_indentation(4, loc1)
    tracker.process_indentation(8, loc2)

    # Dedent back to 0 (should emit 2 DEDENTs)
    tokens = tracker.process_indentation(0, loc3)
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.DEDENT
    assert tokens[1].type == TokenType.DEDENT
    assert tracker.current_level() == 0


def test_partial_dedent(tracker):
    """Test dedent to intermediate level."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)
    loc3 = SourceLocation("test.fusion", 3, 1)
    loc4 = SourceLocation("test.fusion", 4, 1)

    # Indent: 0 → 4 → 8 → 12
    tracker.process_indentation(4, loc1)
    tracker.process_indentation(8, loc2)
    tracker.process_indentation(12, loc3)

    # Dedent back to 4 (should emit 2 DEDENTs)
    tokens = tracker.process_indentation(4, loc4)
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.DEDENT
    assert tokens[1].type == TokenType.DEDENT
    assert tracker.current_level() == 4


def test_dedent_mismatch_error(tracker):
    """Test error on misaligned dedent."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)

    # Indent to 4
    tracker.process_indentation(4, loc1)

    # Try to dedent to 2 (not aligned with any previous level)
    with pytest.raises(LexerError) as exc_info:
        tracker.process_indentation(2, loc2)

    assert "Indentation mismatch" in str(exc_info.value)


# ============================================================
# EOF Handling Tests
# ============================================================

def test_finalize_with_no_indentation(tracker, location):
    """Test finalize with no open blocks."""
    tokens = tracker.finalize(location)
    assert len(tokens) == 0


def test_finalize_with_one_level(tracker):
    """Test finalize with one open block."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 10, 1)

    # Indent to 4
    tracker.process_indentation(4, loc1)

    # Finalize should emit 1 DEDENT
    tokens = tracker.finalize(loc2)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.DEDENT
    assert tracker.current_level() == 0


def test_finalize_with_multiple_levels(tracker):
    """Test finalize with multiple open blocks."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)
    loc3 = SourceLocation("test.fusion", 10, 1)

    # Indent to 4, then 8
    tracker.process_indentation(4, loc1)
    tracker.process_indentation(8, loc2)

    # Finalize should emit 2 DEDENTs
    tokens = tracker.finalize(loc3)
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.DEDENT
    assert tokens[1].type == TokenType.DEDENT
    assert tracker.current_level() == 0


# ============================================================
# Blank Line Detection Tests
# ============================================================

def test_is_blank_line_empty(tracker):
    """Test blank line detection - empty string."""
    assert tracker.is_blank_line("") is True


def test_is_blank_line_spaces(tracker):
    """Test blank line detection - only spaces."""
    assert tracker.is_blank_line("    ") is True


def test_is_blank_line_tabs(tracker):
    """Test blank line detection - only tabs."""
    assert tracker.is_blank_line("\t\t") is True


def test_is_blank_line_mixed_whitespace(tracker):
    """Test blank line detection - mixed whitespace."""
    assert tracker.is_blank_line("  \t  \t  ") is True


def test_is_blank_line_with_code(tracker):
    """Test blank line detection - line with code."""
    assert tracker.is_blank_line("    code") is False


# ============================================================
# Comment Line Detection Tests
# ============================================================

def test_is_comment_line_double_slash(tracker):
    """Test comment detection - // style."""
    assert tracker.is_comment_line("// This is a comment") is True


def test_is_comment_line_single_quote(tracker):
    """Test comment detection - ' style."""
    assert tracker.is_comment_line("' This is a comment") is True


def test_is_comment_line_block_comment(tracker):
    """Test comment detection - /* */ style."""
    assert tracker.is_comment_line("/* This is a comment */") is True


def test_is_comment_line_with_leading_whitespace(tracker):
    """Test comment detection with leading whitespace."""
    assert tracker.is_comment_line("    // Comment") is True


def test_is_comment_line_code_with_trailing_comment(tracker):
    """Test non-comment line with trailing comment."""
    assert tracker.is_comment_line("code // comment") is False


def test_is_comment_line_empty(tracker):
    """Test comment detection on empty line."""
    assert tracker.is_comment_line("") is False


# ============================================================
# Should Skip Line Tests
# ============================================================

def test_should_skip_blank_line(tracker):
    """Test skipping blank lines."""
    assert tracker.should_skip_line("") is True
    assert tracker.should_skip_line("    ") is True


def test_should_skip_comment_line(tracker):
    """Test skipping comment-only lines."""
    assert tracker.should_skip_line("// Comment") is True
    assert tracker.should_skip_line("' Comment") is True


def test_should_not_skip_code_line(tracker):
    """Test not skipping code lines."""
    assert tracker.should_skip_line("print('hello')") is False
    assert tracker.should_skip_line("    code") is False


# ============================================================
# Integration Tests
# ============================================================

def test_complete_indentation_flow(tracker):
    """Test complete indentation workflow."""
    # Simulate this code:
    # if true
    #     if true
    #         print("nested")
    #     print("back")
    # print("done")

    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 2, 1)
    loc3 = SourceLocation("test.fusion", 3, 1)
    loc4 = SourceLocation("test.fusion", 4, 1)
    loc5 = SourceLocation("test.fusion", 5, 1)

    # Line 1: if true (indent 0)
    tokens1 = tracker.process_indentation(0, loc1)
    assert len(tokens1) == 0

    # Line 2: if true (indent 4)
    tokens2 = tracker.process_indentation(4, loc2)
    assert len(tokens2) == 1
    assert tokens2[0].type == TokenType.INDENT

    # Line 3: print("nested") (indent 8)
    tokens3 = tracker.process_indentation(8, loc3)
    assert len(tokens3) == 1
    assert tokens3[0].type == TokenType.INDENT

    # Line 4: print("back") (indent 4)
    tokens4 = tracker.process_indentation(4, loc4)
    assert len(tokens4) == 1
    assert tokens4[0].type == TokenType.DEDENT

    # Line 5: print("done") (indent 0)
    tokens5 = tracker.process_indentation(0, loc5)
    assert len(tokens5) == 1
    assert tokens5[0].type == TokenType.DEDENT


def test_tab_width_configuration():
    """Test custom tab width configuration."""
    tracker = IndentationTracker(tab_width=8)
    location = SourceLocation("test.fusion", 1, 1)

    count, _ = tracker.count_indentation("\tcode", location)
    assert count == 8  # 1 tab = 8 spaces with tab_width=8


def test_repr(tracker):
    """Test string representation."""
    repr_str = repr(tracker)
    assert "IndentationTracker" in repr_str
    assert "stack=[0]" in repr_str
    assert "current=0" in repr_str
