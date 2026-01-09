"""Test suite for comment handling.

Tests all three comment styles: //, ', and /* */
"""

import pytest
from src.lexer.comments import (
    is_comment_start,
    skip_single_line_comment,
    skip_multi_line_comment,
    skip_comment,
    get_comment_type,
)


class TestIsCommentStart:
    """Test comment detection."""

    def test_double_slash_comment(self):
        """Test // comment detection."""
        assert is_comment_start('// comment', 0)
        assert is_comment_start('  // comment', 2)

    def test_single_quote_comment(self):
        """Test ' comment detection - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_multi_line_comment(self):
        """Test /* comment detection."""
        assert is_comment_start('/* comment */', 0)
        assert is_comment_start('  /* comment */', 2)

    def test_not_comment(self):
        """Test non-comment text."""
        assert not is_comment_start('int x', 0)
        assert not is_comment_start('x = 5', 0)
        assert not is_comment_start('', 0)

    def test_slash_without_slash(self):
        """Test single / is not a comment."""
        assert not is_comment_start('/ 5', 0)
        assert not is_comment_start('/= 5', 0)

    def test_position_at_end(self):
        """Test position at end of text."""
        assert not is_comment_start('abc', 3)
        assert not is_comment_start('abc', 10)


class TestSingleLineComments:
    """Test single-line comment skipping."""

    def test_double_slash_basic(self):
        """Test basic // comment."""
        pos, lines = skip_single_line_comment('// comment\ncode', 0)
        assert pos == 10  # Points to \n
        assert lines == 0

    def test_double_slash_at_eof(self):
        """Test // comment at end of file."""
        pos, lines = skip_single_line_comment('// comment', 0)
        assert pos == 10  # Points to EOF
        assert lines == 0

    def test_double_slash_empty(self):
        """Test empty // comment."""
        pos, lines = skip_single_line_comment('//\ncode', 0)
        assert pos == 2  # Points to \n
        assert lines == 0

    def test_single_quote_basic(self):
        """Test basic ' comment - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_single_quote_at_eof(self):
        """Test ' comment at end of file - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_single_quote_empty(self):
        """Test empty ' comment - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_comment_with_code_after(self):
        """Test comment followed by code."""
        pos, lines = skip_single_line_comment('// test\nint x = 5', 0)
        assert pos == 7  # Points to \n
        assert lines == 0

    def test_not_comment(self):
        """Test non-comment returns original position."""
        pos, lines = skip_single_line_comment('int x', 0)
        assert pos == 0
        assert lines == 0


class TestMultiLineComments:
    """Test multi-line comment skipping."""

    def test_basic_multi_line(self):
        """Test basic /* */ comment."""
        pos, lines = skip_multi_line_comment('/* comment */code', 0)
        assert pos == 13  # After */
        assert lines == 0

    def test_multi_line_with_newlines(self):
        """Test /* */ with newlines."""
        pos, lines = skip_multi_line_comment('/* line1\nline2 */code', 0)
        assert pos == 17  # After */
        assert lines == 1

    def test_multi_line_multiple_newlines(self):
        """Test /* */ with multiple newlines."""
        pos, lines = skip_multi_line_comment('/* line1\nline2\nline3 */code', 0)
        assert pos == 23  # After */
        assert lines == 2

    def test_empty_multi_line(self):
        """Test empty /* */ comment."""
        pos, lines = skip_multi_line_comment('/**/code', 0)
        assert pos == 4  # After */
        assert lines == 0

    def test_multi_line_with_asterisks(self):
        """Test /* */ with asterisks inside."""
        pos, lines = skip_multi_line_comment('/* * * * */code', 0)
        assert pos == 11  # After */
        assert lines == 0

    def test_multi_line_with_slashes(self):
        """Test /* */ with slashes inside."""
        pos, lines = skip_multi_line_comment('/* / / / */code', 0)
        assert pos == 11  # After */
        assert lines == 0

    def test_multi_line_almost_closing(self):
        """Test /* */ with almost-closing sequences."""
        pos, lines = skip_multi_line_comment('/* * / * */code', 0)
        assert pos == 11  # After */
        assert lines == 0

    def test_unterminated_comment(self):
        """Test error on unterminated comment."""
        with pytest.raises(ValueError, match="Unterminated"):
            skip_multi_line_comment('/* unterminated', 0)

    def test_unterminated_with_newlines(self):
        """Test error on unterminated comment with newlines."""
        with pytest.raises(ValueError, match="Unterminated"):
            skip_multi_line_comment('/* line1\nline2\nunterminated', 0)

    def test_not_multi_line_comment(self):
        """Test non-comment returns original position."""
        pos, lines = skip_multi_line_comment('int x', 0)
        assert pos == 0
        assert lines == 0


class TestSkipComment:
    """Test unified comment skipping function."""

    def test_skip_double_slash(self):
        """Test skipping // comment."""
        result = skip_comment('// comment\ncode', 0)
        assert result is not None
        pos, lines = result
        assert pos == 10
        assert lines == 0

    def test_skip_single_quote(self):
        """Test skipping ' comment - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_skip_multi_line(self):
        """Test skipping /* */ comment."""
        result = skip_comment('/* comment */code', 0)
        assert result is not None
        pos, lines = result
        assert pos == 13
        assert lines == 0

    def test_skip_multi_line_with_newlines(self):
        """Test skipping /* */ with newlines."""
        result = skip_comment('/* line1\nline2 */code', 0)
        assert result is not None
        pos, lines = result
        assert pos == 17
        assert lines == 1

    def test_not_comment(self):
        """Test non-comment returns None."""
        result = skip_comment('int x', 0)
        assert result is None

    def test_at_different_positions(self):
        """Test skipping at different positions."""
        # // at position 5
        result = skip_comment('int x // comment\ncode', 6)
        assert result is not None
        pos, lines = result
        assert pos == 16

    def test_unterminated_multi_line_error(self):
        """Test error on unterminated /* */."""
        with pytest.raises(ValueError, match="Unterminated"):
            skip_comment('/* unterminated', 0)


class TestGetCommentType:
    """Test comment type detection."""

    def test_double_slash_type(self):
        """Test // detected as single."""
        assert get_comment_type('// comment', 0) == 'single'

    def test_single_quote_type(self):
        """Test ' detected as single - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_multi_line_type(self):
        """Test /* detected as multi."""
        assert get_comment_type('/* comment */', 0) == 'multi'

    def test_not_comment_type(self):
        """Test non-comment returns None."""
        assert get_comment_type('int x', 0) is None

    def test_slash_not_comment(self):
        """Test single / is not a comment."""
        assert get_comment_type('/ 5', 0) is None

    def test_type_at_position(self):
        """Test type detection at different positions."""
        assert get_comment_type('int x // comment', 6) == 'single'
        # ' comment test removed - disabled for char literal support
        assert get_comment_type('int x /* comment */', 6) == 'multi'


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_comment_at_end_of_text(self):
        """Test comment at end with no trailing newline."""
        result = skip_comment('// comment', 0)
        assert result is not None
        pos, lines = result
        assert pos == 10

    def test_multiple_slashes(self):
        """Test multiple slashes in comment."""
        result = skip_comment('/// comment\ncode', 0)
        assert result is not None
        pos, lines = result
        assert pos == 11

    def test_quote_in_double_slash(self):
        """Test ' inside // comment."""
        result = skip_comment("// comment with ' quote\ncode", 0)
        assert result is not None
        pos, lines = result
        assert pos == 23

    def test_double_slash_in_quote(self):
        """Test // inside ' comment - DISABLED."""
        pytest.skip("' comment support disabled for char literal support")

    def test_nested_multi_line_not_supported(self):
        """Test that /* /* */ ends at first */."""
        result = skip_comment('/* /* nested */ still comment */code', 0)
        assert result is not None
        pos, lines = result
        # Should end at first */
        assert pos == 15

    def test_comment_with_special_chars(self):
        """Test comments with special characters."""
        result = skip_comment('// !@#$%^&*()_+-={}[]|\\:";\'<>?,./\ncode', 0)
        assert result is not None
        assert result[0] == 33  # Points to \n

    def test_empty_text(self):
        """Test empty text."""
        result = skip_comment('', 0)
        assert result is None

    def test_position_beyond_text(self):
        """Test position beyond text length."""
        result = skip_comment('abc', 10)
        assert result is None

    def test_multi_line_only_newlines(self):
        """Test /* */ with only newlines."""
        result = skip_comment('/*\n\n\n*/code', 0)
        assert result is not None
        pos, lines = result
        assert pos == 7
        assert lines == 3

    def test_multi_line_at_eof(self):
        """Test complete /* */ at end of file."""
        result = skip_comment('/* comment */', 0)
        assert result is not None
        pos, lines = result
        assert pos == 13
        assert lines == 0


class TestRealWorldScenarios:
    """Test real-world comment scenarios."""

    def test_inline_comment(self):
        """Test inline comment after code."""
        # Comment starts at position 10
        result = skip_comment('int x = 5; // explanation\nint y = 10', 11)
        assert result is not None
        pos, lines = result
        assert pos == 25

    def test_doc_comment_style(self):
        """Test documentation-style comment."""
        result = skip_comment('/// This is a doc comment\nfunction foo()', 0)
        assert result is not None
        pos, lines = result
        assert pos == 25

    def test_commented_out_code(self):
        """Test commented out code."""
        result = skip_comment('// int x = 5;\nint y = 10', 0)
        assert result is not None
        pos, lines = result
        assert pos == 13

    def test_header_comment_block(self):
        """Test header comment block."""
        text = '''/*
 * File: main.fusion
 * Author: John Doe
 * Date: 2025-01-01
 */
int main()'''
        result = skip_comment(text, 0)
        assert result is not None
        pos, lines = result
        assert lines == 4  # 4 newlines in comment

    def test_separator_comment(self):
        """Test separator comment."""
        result = skip_comment('// ==========================================\ncode', 0)
        assert result is not None
        pos, lines = result
        assert pos == 45
