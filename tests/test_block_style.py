"""Unit tests for BlockStyleTracker class.

Tests the block style detection and management system for Fusion's
three block syntaxes: indentation, braces, and End keywords.
"""

import pytest
from src.lexer.block_style import BlockStyleTracker, BlockStyle, BlockStyleError


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def tracker():
    """Create a fresh BlockStyleTracker for each test."""
    return BlockStyleTracker()


# ============================================================
# Initialization Tests
# ============================================================

def test_initialization(tracker):
    """Test BlockStyleTracker initialization."""
    assert tracker.brace_depth == 0
    assert tracker.block_stack == []
    assert tracker.current_block_style() is None
    assert tracker.should_track_indentation() is True


def test_reset(tracker):
    """Test reset method."""
    # Add some blocks
    tracker.enter_brace_block()
    tracker.enter_indent_block()

    # Reset should clear everything
    tracker.reset()
    assert tracker.brace_depth == 0
    assert tracker.block_stack == []


# ============================================================
# Brace Block Tests
# ============================================================

def test_enter_brace_block(tracker):
    """Test entering a brace block."""
    tracker.enter_brace_block()

    assert tracker.brace_depth == 1
    assert tracker.current_block_style() == BlockStyle.BRACE
    assert tracker.is_inside_brace_block() is True
    assert tracker.should_track_indentation() is False


def test_exit_brace_block(tracker):
    """Test exiting a brace block."""
    tracker.enter_brace_block()
    tracker.exit_brace_block()

    assert tracker.brace_depth == 0
    assert tracker.current_block_style() is None
    assert tracker.is_inside_brace_block() is False
    assert tracker.should_track_indentation() is True


def test_nested_brace_blocks(tracker):
    """Test nested brace blocks."""
    tracker.enter_brace_block()
    assert tracker.brace_depth == 1

    tracker.enter_brace_block()
    assert tracker.brace_depth == 2

    tracker.exit_brace_block()
    assert tracker.brace_depth == 1

    tracker.exit_brace_block()
    assert tracker.brace_depth == 0


def test_unmatched_closing_brace_error(tracker):
    """Test error on unmatched closing brace."""
    with pytest.raises(BlockStyleError) as exc_info:
        tracker.exit_brace_block()

    assert "Unexpected closing brace" in str(exc_info.value)


def test_indentation_disabled_in_braces(tracker):
    """Test that indentation tracking is disabled inside braces."""
    assert tracker.should_track_indentation() is True

    tracker.enter_brace_block()
    assert tracker.should_track_indentation() is False

    tracker.exit_brace_block()
    assert tracker.should_track_indentation() is True


# ============================================================
# Indent Block Tests
# ============================================================

def test_enter_indent_block(tracker):
    """Test entering an indentation block."""
    tracker.enter_indent_block()

    assert tracker.current_block_style() == BlockStyle.INDENT
    assert len(tracker.block_stack) == 1


def test_exit_indent_block(tracker):
    """Test exiting an indentation block."""
    tracker.enter_indent_block()
    tracker.exit_indent_block()

    assert tracker.current_block_style() is None
    assert len(tracker.block_stack) == 0


def test_nested_indent_blocks(tracker):
    """Test nested indentation blocks."""
    tracker.enter_indent_block()
    assert len(tracker.block_stack) == 1

    tracker.enter_indent_block()
    assert len(tracker.block_stack) == 2

    tracker.exit_indent_block()
    assert len(tracker.block_stack) == 1

    tracker.exit_indent_block()
    assert len(tracker.block_stack) == 0


def test_indent_ignored_inside_braces(tracker):
    """Test that indent blocks are ignored inside brace blocks."""
    tracker.enter_brace_block()

    # Try to enter indent block (should be ignored)
    tracker.enter_indent_block()

    # Should still only have the brace block
    assert tracker.current_block_style() == BlockStyle.BRACE
    assert len(tracker.block_stack) == 1


# ============================================================
# End Keyword Block Tests
# ============================================================

def test_enter_end_keyword_block(tracker):
    """Test entering an End keyword block."""
    tracker.enter_end_keyword_block()

    assert tracker.current_block_style() == BlockStyle.END_KEYWORD
    assert len(tracker.block_stack) == 1


def test_exit_end_keyword_block(tracker):
    """Test exiting an End keyword block."""
    tracker.enter_end_keyword_block()
    tracker.exit_end_keyword_block()

    assert tracker.current_block_style() is None
    assert len(tracker.block_stack) == 0


def test_nested_end_keyword_blocks(tracker):
    """Test nested End keyword blocks."""
    tracker.enter_end_keyword_block()
    assert len(tracker.block_stack) == 1

    tracker.enter_end_keyword_block()
    assert len(tracker.block_stack) == 2

    tracker.exit_end_keyword_block()
    assert len(tracker.block_stack) == 1

    tracker.exit_end_keyword_block()
    assert len(tracker.block_stack) == 0


def test_unmatched_end_keyword_error(tracker):
    """Test error on unmatched End keyword."""
    with pytest.raises(BlockStyleError) as exc_info:
        tracker.exit_end_keyword_block()

    assert "Unexpected 'End' keyword" in str(exc_info.value)


# ============================================================
# Mixed Block Style Tests
# ============================================================

def test_brace_inside_indent_block(tracker):
    """Test brace block inside indent block."""
    tracker.enter_indent_block()
    assert tracker.current_block_style() == BlockStyle.INDENT

    tracker.enter_brace_block()
    assert tracker.current_block_style() == BlockStyle.BRACE

    tracker.exit_brace_block()
    assert tracker.current_block_style() == BlockStyle.INDENT

    tracker.exit_indent_block()
    assert tracker.current_block_style() is None


def test_indent_then_end_keyword(tracker):
    """Test indent block followed by end keyword block."""
    tracker.enter_indent_block()
    tracker.exit_indent_block()

    tracker.enter_end_keyword_block()
    assert tracker.current_block_style() == BlockStyle.END_KEYWORD

    tracker.exit_end_keyword_block()
    assert tracker.current_block_style() is None


def test_all_three_styles_nested(tracker):
    """Test all three block styles nested."""
    # Indent block
    tracker.enter_indent_block()
    assert tracker.current_block_style() == BlockStyle.INDENT

    # End keyword inside indent
    tracker.enter_end_keyword_block()
    assert tracker.current_block_style() == BlockStyle.END_KEYWORD

    # Brace inside End keyword
    tracker.enter_brace_block()
    assert tracker.current_block_style() == BlockStyle.BRACE

    # Exit in reverse order
    tracker.exit_brace_block()
    assert tracker.current_block_style() == BlockStyle.END_KEYWORD

    tracker.exit_end_keyword_block()
    assert tracker.current_block_style() == BlockStyle.INDENT

    tracker.exit_indent_block()
    assert tracker.current_block_style() is None


# ============================================================
# Validation Tests
# ============================================================

def test_validate_closing_brace(tracker):
    """Test validation of brace block closing."""
    tracker.enter_brace_block()

    assert tracker.validate_closing(BlockStyle.BRACE) is True
    assert tracker.validate_closing(BlockStyle.INDENT) is False
    assert tracker.validate_closing(BlockStyle.END_KEYWORD) is False


def test_validate_closing_indent(tracker):
    """Test validation of indent block closing."""
    tracker.enter_indent_block()

    assert tracker.validate_closing(BlockStyle.INDENT) is True
    assert tracker.validate_closing(BlockStyle.BRACE) is False
    assert tracker.validate_closing(BlockStyle.END_KEYWORD) is False


def test_validate_closing_end_keyword(tracker):
    """Test validation of End keyword block closing."""
    tracker.enter_end_keyword_block()

    assert tracker.validate_closing(BlockStyle.END_KEYWORD) is True
    assert tracker.validate_closing(BlockStyle.BRACE) is False
    assert tracker.validate_closing(BlockStyle.INDENT) is False


def test_validate_closing_no_blocks(tracker):
    """Test validation when no blocks are open."""
    assert tracker.validate_closing(BlockStyle.BRACE) is False
    assert tracker.validate_closing(BlockStyle.INDENT) is False
    assert tracker.validate_closing(BlockStyle.END_KEYWORD) is False


# ============================================================
# State Query Tests
# ============================================================

def test_has_open_blocks_false(tracker):
    """Test has_open_blocks when no blocks are open."""
    assert tracker.has_open_blocks() is False


def test_has_open_blocks_with_indent(tracker):
    """Test has_open_blocks with indent block."""
    tracker.enter_indent_block()
    assert tracker.has_open_blocks() is True


def test_has_open_blocks_with_brace(tracker):
    """Test has_open_blocks with brace block."""
    tracker.enter_brace_block()
    assert tracker.has_open_blocks() is True


def test_has_open_blocks_with_end_keyword(tracker):
    """Test has_open_blocks with End keyword block."""
    tracker.enter_end_keyword_block()
    assert tracker.has_open_blocks() is True


def test_current_block_style_empty(tracker):
    """Test current_block_style with no blocks."""
    assert tracker.current_block_style() is None


def test_is_inside_brace_block_false(tracker):
    """Test is_inside_brace_block when outside braces."""
    assert tracker.is_inside_brace_block() is False

    # Enter indent block (not a brace)
    tracker.enter_indent_block()
    assert tracker.is_inside_brace_block() is False


def test_is_inside_brace_block_true(tracker):
    """Test is_inside_brace_block when inside braces."""
    tracker.enter_brace_block()
    assert tracker.is_inside_brace_block() is True


# ============================================================
# Edge Case Tests
# ============================================================

def test_multiple_brace_exits(tracker):
    """Test that multiple brace exits fail after all opened braces closed."""
    tracker.enter_brace_block()
    tracker.exit_brace_block()

    # Second exit should raise error
    with pytest.raises(BlockStyleError):
        tracker.exit_brace_block()


def test_multiple_end_keyword_exits(tracker):
    """Test that multiple End exits fail after all blocks closed."""
    tracker.enter_end_keyword_block()
    tracker.exit_end_keyword_block()

    # Second exit should raise error
    with pytest.raises(BlockStyleError):
        tracker.exit_end_keyword_block()


def test_repr(tracker):
    """Test string representation."""
    repr_str = repr(tracker)
    assert "BlockStyleTracker" in repr_str
    assert "brace_depth=0" in repr_str
    assert "current=None" in repr_str

    # Add a block and check repr again
    tracker.enter_brace_block()
    repr_str = repr(tracker)
    assert "brace_depth=1" in repr_str
    assert "BRACE" in repr_str
