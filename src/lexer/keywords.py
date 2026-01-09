"""Keyword recognition for Fusion lexer.

This module provides keyword lookup functionality to distinguish between
Fusion's reserved keywords and user-defined identifiers.

Total Keywords: 65 (including special cases like 'Enum')
"""

from src.lexer.token import TokenType
from typing import Dict


# Complete keyword lookup table mapping keyword strings to TokenTypes
KEYWORDS: Dict[str, TokenType] = {
    # ============================================================
    # Control Flow Keywords (11)
    # ============================================================
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'while': TokenType.WHILE,
    'loop': TokenType.LOOP,
    'end': TokenType.END,
    'End': TokenType.END,           # Special case: capital 'E' allowed (VB.NET style)
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'return': TokenType.RETURN,
    'match': TokenType.MATCH,
    'case': TokenType.CASE,

    # ============================================================
    # Function Keywords (4)
    # ============================================================
    'function': TokenType.FUNCTION,
    'func': TokenType.FUNC,
    'async': TokenType.ASYNC,
    'await': TokenType.AWAIT,

    # ============================================================
    # OOP Keywords (9)
    # ============================================================
    'class': TokenType.CLASS,
    'struct': TokenType.STRUCT,
    'interface': TokenType.INTERFACE,
    'enum': TokenType.ENUM,         # lowercase 'enum' for MVP consistency
    'Enum': TokenType.ENUM,         # Special case: capital 'E' allowed
    'inherits': TokenType.INHERITS,
    'implements': TokenType.IMPLEMENTS,
    'property': TokenType.PROPERTY,
    'get': TokenType.GET,
    'set': TokenType.SET,

    # ============================================================
    # Modifier Keywords (8)
    # ============================================================
    'public': TokenType.PUBLIC,
    'private': TokenType.PRIVATE,
    'protected': TokenType.PROTECTED,
    'static': TokenType.STATIC,
    'virtual': TokenType.VIRTUAL,
    'override': TokenType.OVERRIDE,
    'abstract': TokenType.ABSTRACT,
    'sealed': TokenType.SEALED,

    # ============================================================
    # Type Keywords (10)
    # ============================================================
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'double': TokenType.DOUBLE,
    'string': TokenType.STRING,
    'bool': TokenType.BOOL,
    'char': TokenType.CHAR,
    'byte': TokenType.BYTE,
    'short': TokenType.SHORT,
    'long': TokenType.LONG,
    'void': TokenType.VOID,

    # ============================================================
    # Memory Management Keywords (3)
    # ============================================================
    'Unique': TokenType.UNIQUE,     # Capital U required
    'Shared': TokenType.SHARED,     # Capital S required
    'Weak': TokenType.WEAK,         # Capital W required

    # ============================================================
    # Variable Keywords (2)
    # ============================================================
    'var': TokenType.VAR,
    'const': TokenType.CONST,

    # ============================================================
    # Literal Keywords (4)
    # ============================================================
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
    'this': TokenType.THIS,

    # ============================================================
    # Word-based Operator Keywords (5)
    # ============================================================
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'is': TokenType.IS,
    'in': TokenType.IN,

    # ============================================================
    # Other Keywords (9)
    # ============================================================
    'import': TokenType.IMPORT,
    'new': TokenType.NEW,
    'cast': TokenType.CAST,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'finally': TokenType.FINALLY,
    'throw': TokenType.THROW,
    'Error': TokenType.ERROR,       # Capital E required for Error type
    'go': TokenType.GO,
}


def is_keyword(word: str) -> bool:
    """Check if a word is a Fusion keyword.

    Args:
        word: The string to check

    Returns:
        True if word is a reserved keyword, False otherwise

    Examples:
        >>> is_keyword('if')
        True
        >>> is_keyword('myVariable')
        False
        >>> is_keyword('Enum')  # Special case: capital E allowed
        True
        >>> is_keyword('INT')   # All caps not allowed
        False
    """
    return word in KEYWORDS


def get_keyword_type(word: str) -> TokenType:
    """Get the TokenType for a keyword, or IDENTIFIER if not a keyword.

    This is the primary function used by the lexer to determine if an
    alphanumeric sequence is a keyword or an identifier.

    Args:
        word: The string to look up

    Returns:
        TokenType for the keyword if it exists, otherwise TokenType.IDENTIFIER

    Examples:
        >>> get_keyword_type('if')
        TokenType.IF
        >>> get_keyword_type('class')
        TokenType.CLASS
        >>> get_keyword_type('myVariable')
        TokenType.IDENTIFIER
        >>> get_keyword_type('Enum')
        TokenType.ENUM
        >>> get_keyword_type('INT')  # Not a keyword (case-sensitive)
        TokenType.IDENTIFIER
    """
    return KEYWORDS.get(word, TokenType.IDENTIFIER)


# Expose keyword count for documentation and testing
KEYWORD_COUNT = len(KEYWORDS)
