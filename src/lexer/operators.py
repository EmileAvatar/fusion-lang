"""Operator tokenization for Fusion lexer.

This module provides operator recognition using longest-match algorithm
to correctly handle multi-character operators like '...', '**=', '?.', etc.

Total Operators: 30 operator token types (excluding delimiters)
Total Delimiters: 10 delimiter token types
"""

from src.lexer.token import TokenType
from typing import Dict, Optional, Tuple


# ============================================================
# Three-character operators (checked first for longest-match)
# ============================================================
THREE_CHAR_OPERATORS: Dict[str, TokenType] = {
    '...': TokenType.RANGE,        # Range operator
    '**=': TokenType.POWER_ASSIGN, # Power assignment
}


# ============================================================
# Two-character operators (checked after 3-char)
# ============================================================
TWO_CHAR_OPERATORS: Dict[str, TokenType] = {
    # Comparison operators
    '==': TokenType.EQUAL,
    '!=': TokenType.NOT_EQUAL,
    '<>': TokenType.NOT_EQUAL_ALT,  # Alternative syntax
    '<=': TokenType.LESS_EQUAL,
    '>=': TokenType.GREATER_EQUAL,

    # Logical operators
    '&&': TokenType.LOGICAL_AND,
    '||': TokenType.LOGICAL_OR,

    # Assignment operators
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MULTIPLY_ASSIGN,
    '/=': TokenType.DIVIDE_ASSIGN,
    '%=': TokenType.MODULO_ASSIGN,

    # Arithmetic operators
    '**': TokenType.POWER,
    '++': TokenType.INCREMENT,
    '--': TokenType.DECREMENT,

    # Special operators
    '?.': TokenType.SAFE_NAV,      # Safe navigation
    '?[': TokenType.SAFE_INDEX,    # Safe indexing
    '<-': TokenType.CHANNEL_SEND,  # Channel send (Go-style)
    '->': TokenType.ARROW,         # Arrow (various uses)
}


# ============================================================
# Single-character operators
# ============================================================
SINGLE_CHAR_OPERATORS: Dict[str, TokenType] = {
    # Arithmetic
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,

    # Comparison
    '<': TokenType.LESS,
    '>': TokenType.GREATER,

    # Assignment
    '=': TokenType.ASSIGN,

    # Logical
    '!': TokenType.LOGICAL_NOT,
}


# ============================================================
# Delimiters (treated like operators for tokenization)
# ============================================================
DELIMITERS: Dict[str, TokenType] = {
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
    '.': TokenType.DOT,
    '?': TokenType.QUESTION,
}


# ============================================================
# Helper Functions
# ============================================================

def is_operator_char(char: str) -> bool:
    """Check if a character can be part of an operator.

    Args:
        char: Single character to check

    Returns:
        True if char is used in any operator

    Examples:
        >>> is_operator_char('+')
        True
        >>> is_operator_char('a')
        False
    """
    if not char or len(char) != 1:
        return False

    return (char in SINGLE_CHAR_OPERATORS or
            char in DELIMITERS or
            char in '+-*/<>=!&|?.%:')


def match_operator(text: str, position: int) -> Optional[Tuple[TokenType, str, int]]:
    """Match an operator at the given position using longest-match algorithm.

    This function implements the longest-match algorithm by trying to match
    operators in order of decreasing length (3-char, then 2-char, then 1-char).

    Args:
        text: The source code text
        position: Current position in text

    Returns:
        Tuple of (TokenType, matched_string, new_position) if match found, None otherwise

    Examples:
        >>> match_operator('...', 0)
        (TokenType.RANGE, '...', 3)
        >>> match_operator('**=', 0)
        (TokenType.POWER_ASSIGN, '**=', 3)
        >>> match_operator('==', 0)
        (TokenType.EQUAL, '==', 2)
        >>> match_operator('+', 0)
        (TokenType.PLUS, '+', 1)
    """
    remaining = text[position:]

    # Try 3-character operators first (longest-match)
    if len(remaining) >= 3:
        three_char = remaining[:3]
        if three_char in THREE_CHAR_OPERATORS:
            return (THREE_CHAR_OPERATORS[three_char], three_char, position + 3)

    # Try 2-character operators
    if len(remaining) >= 2:
        two_char = remaining[:2]
        if two_char in TWO_CHAR_OPERATORS:
            return (TWO_CHAR_OPERATORS[two_char], two_char, position + 2)

    # Try single-character operators
    if len(remaining) >= 1:
        one_char = remaining[0]

        # Check operators first
        if one_char in SINGLE_CHAR_OPERATORS:
            return (SINGLE_CHAR_OPERATORS[one_char], one_char, position + 1)

        # Check delimiters
        if one_char in DELIMITERS:
            return (DELIMITERS[one_char], one_char, position + 1)

    return None


def is_delimiter(token_type: TokenType) -> bool:
    """Check if a TokenType is a delimiter.

    Args:
        token_type: TokenType to check

    Returns:
        True if token_type is a delimiter
    """
    return token_type in {
        TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACKET, TokenType.RBRACKET,
        TokenType.LBRACE, TokenType.RBRACE,
        TokenType.COMMA, TokenType.COLON,
        TokenType.DOT, TokenType.QUESTION,
    }


def is_operator(token_type: TokenType) -> bool:
    """Check if a TokenType is an operator (excludes delimiters).

    Args:
        token_type: TokenType to check

    Returns:
        True if token_type is an operator (not a delimiter)
    """
    operator_types = {
        # Arithmetic
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
        TokenType.DIVIDE, TokenType.MODULO, TokenType.POWER,

        # Comparison
        TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL,
        TokenType.GREATER_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL,
        TokenType.NOT_EQUAL_ALT,

        # Logical
        TokenType.LOGICAL_AND, TokenType.LOGICAL_OR, TokenType.LOGICAL_NOT,

        # Assignment
        TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
        TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN,
        TokenType.MODULO_ASSIGN, TokenType.POWER_ASSIGN,

        # Special
        TokenType.RANGE, TokenType.SAFE_NAV, TokenType.SAFE_INDEX,
        TokenType.CHANNEL_SEND, TokenType.ARROW,
        TokenType.INCREMENT, TokenType.DECREMENT,
    }
    return token_type in operator_types


# Count of operators for testing
OPERATOR_COUNT = (
    len(THREE_CHAR_OPERATORS) +
    len(TWO_CHAR_OPERATORS) +
    len(SINGLE_CHAR_OPERATORS)
)

DELIMITER_COUNT = len(DELIMITERS)
TOTAL_OPERATOR_AND_DELIMITER_COUNT = OPERATOR_COUNT + DELIMITER_COUNT
