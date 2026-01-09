"""Block style tracking for Fusion's three block syntaxes.

This module manages the three block styles supported by Fusion:
1. Indentation-based (Python-style)
2. Brace-based (C/Java-style with {})
3. End keyword-based (VB.NET-style with 'End function', 'End if', etc.)

The tracker handles mixed styles in the same file and determines when
indentation tracking should be active or disabled.
"""

from typing import List, Optional
from enum import Enum, auto


class BlockStyle(Enum):
    """Enumeration of block styles in Fusion."""
    INDENT = auto()     # Python-style indentation blocks
    BRACE = auto()      # C-style brace blocks
    END_KEYWORD = auto()  # VB.NET-style End keyword blocks


class BlockStyleError(Exception):
    """Raised when block style nesting is invalid."""
    pass


class BlockStyleTracker:
    """Tracks block styles and manages nesting.

    Fusion allows mixing all three block styles in the same file.
    This tracker:
    - Tracks brace depth (for {} blocks)
    - Tracks block style stack for proper nesting
    - Determines when indentation tracking should be disabled
    - Validates block closure (e.g., can't close indent block with })

    Attributes:
        brace_depth: Current nesting depth of brace blocks
        block_stack: Stack of active block styles
    """

    def __init__(self):
        """Initialize the block style tracker."""
        self.brace_depth: int = 0
        self.block_stack: List[BlockStyle] = []

    def reset(self) -> None:
        """Reset tracker to initial state."""
        self.brace_depth = 0
        self.block_stack = []

    def enter_brace_block(self) -> None:
        """Enter a brace-delimited block.

        Called when a '{' is encountered.
        """
        self.brace_depth += 1
        self.block_stack.append(BlockStyle.BRACE)

    def exit_brace_block(self) -> None:
        """Exit a brace-delimited block.

        Called when a '}' is encountered.

        Raises:
            BlockStyleError: If no matching opening brace exists
        """
        if self.brace_depth == 0:
            raise BlockStyleError("Unexpected closing brace '}' with no matching '{'")

        self.brace_depth -= 1

        # Pop brace block from stack
        if self.block_stack and self.block_stack[-1] == BlockStyle.BRACE:
            self.block_stack.pop()

    def enter_indent_block(self) -> None:
        """Enter an indentation-based block.

        Called when an INDENT token is emitted.
        Only allowed outside of brace blocks.
        """
        if not self.should_track_indentation():
            # Inside brace block, don't track indentation
            return

        self.block_stack.append(BlockStyle.INDENT)

    def exit_indent_block(self) -> None:
        """Exit an indentation-based block.

        Called when a DEDENT token is emitted.
        """
        if self.block_stack and self.block_stack[-1] == BlockStyle.INDENT:
            self.block_stack.pop()

    def enter_end_keyword_block(self) -> None:
        """Enter an End keyword-based block.

        Called when a block starts that will be closed with 'End'.
        Examples: function, if, while, for, etc.
        """
        self.block_stack.append(BlockStyle.END_KEYWORD)

    def exit_end_keyword_block(self) -> None:
        """Exit an End keyword-based block.

        Called when an 'End' keyword is encountered.

        Raises:
            BlockStyleError: If no matching End keyword block exists
        """
        if not self.block_stack or self.block_stack[-1] != BlockStyle.END_KEYWORD:
            raise BlockStyleError("Unexpected 'End' keyword with no matching block start")

        self.block_stack.pop()

    def should_track_indentation(self) -> bool:
        """Check if indentation tracking should be active.

        Indentation tracking is disabled inside brace blocks,
        since braces handle block structure explicitly.

        Returns:
            True if indentation should be tracked, False otherwise
        """
        return self.brace_depth == 0

    def is_inside_brace_block(self) -> bool:
        """Check if currently inside a brace block.

        Returns:
            True if inside one or more brace blocks
        """
        return self.brace_depth > 0

    def current_block_style(self) -> Optional[BlockStyle]:
        """Get the current active block style.

        Returns:
            The topmost block style on the stack, or None if stack is empty
        """
        if self.block_stack:
            return self.block_stack[-1]
        return None

    def has_open_blocks(self) -> bool:
        """Check if there are any open blocks.

        Returns:
            True if there are unclosed blocks
        """
        return len(self.block_stack) > 0 or self.brace_depth > 0

    def validate_closing(self, closing_style: BlockStyle) -> bool:
        """Validate that a closing matches the current block style.

        Args:
            closing_style: The block style being closed

        Returns:
            True if valid, False otherwise
        """
        current = self.current_block_style()
        if current is None:
            return False

        # Can only close blocks with matching style
        return current == closing_style

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"BlockStyleTracker("
            f"brace_depth={self.brace_depth}, "
            f"stack={[s.name for s in self.block_stack]}, "
            f"current={self.current_block_style().name if self.current_block_style() else 'None'}"
            f")"
        )
