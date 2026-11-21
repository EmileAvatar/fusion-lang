"""Keyword recognition for Fusion lexer.

This module provides keyword lookup functionality to distinguish between
Fusion's reserved keywords and user-defined identifiers.

Keywords: KEYWORD_COUNT (70, including the special cases 'Enum' and 'End'). `end` is a keyword
again (Task 61, D.162): it closes a block like `End` and is never a name.

RESERVED_WORDS (Task 61): words kept for a planned feature or for the future. They are not
keywords yet - using one as a name is an error that says what it is kept for. After a `.`
any word, reserved or a keyword, is a member name (`m.type`, `x.default`).
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
    'End': TokenType.END,           # Special case: capital 'E' allowed (VB.NET style)
    'end': TokenType.END,           # a keyword again (Task 61, D.162) - never a name
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
    # Modifier Keywords (10)
    # ============================================================
    'public': TokenType.PUBLIC,
    'private': TokenType.PRIVATE,
    'internal': TokenType.INTERNAL,     # Task 32.2h
    'namespace': TokenType.NAMESPACE,   # Task 32.2h
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
    # Memory Management Keywords (2) - `Unique` released (Task 48.8, D.080): every object moves
    # ============================================================
    'Shared': TokenType.SHARED,     # Capital S required
    'Weak': TokenType.WEAK,         # Capital W required

    # ============================================================
    # Variable Keywords (3) - let / var reserved again for Task 46 (user, 2026-10-29)
    # ============================================================
    'const': TokenType.CONST,
    'let': TokenType.LET,
    'var': TokenType.VAR,
    'service': TokenType.SERVICE,   # reserved for services (Task 42)
    'fixed': TokenType.FIXED,       # an array that never changes size (Task 45.14, D.141); fixed(n) - 47.5

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
    # Other Keywords (8) - Error is a built-in type name, like List (Task 26)
    # ============================================================
    'import': TokenType.IMPORT,
    'new': TokenType.NEW,
    'cast': TokenType.CAST,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'finally': TokenType.FINALLY,
    'throw': TokenType.THROW,
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


# Words reserved for a planned Fusion feature (Task 61, D.162) - the value says which
_FOR_A_FEATURE = {
    'check': 'loop safety checks (Task 56)',
    'unsafe': 'unsafe blocks (Task 42.40)',
    'hotpath': 'hot-path services (Task 42.23)',
    'extern': 'calling C libraries (extern "C")',
    'switch': 'an alias of match (D.065)',
    'elif': 'an alias of else if (SYN.018)',
    'assert': 'assert (SYN.023)',
    'channel': 'channels in a service (Task 42.34)',
    'lock': 'locks inside unsafe (Task 42.38)',
    'where': 'conditions on generic types (Task 33)',
    'defer': 'clean-up written next to the set-up (an idea)',
    'comptime': 'code run while compiling (an idea)',
    'union': 'an enum with data (an idea)',
    'choice': 'an enum with data (an idea)',
    'operator': 'operator overloading (an idea)',
    'yield': 'generators (an idea)',
}

# Words reserved for the future, from other languages (Task 61, D.162)
_FOR_THE_FUTURE = (
    'module', 'export', 'using', 'default', 'typeof', 'sizeof', 'nameof', 'select', 'atomic',
    'transaction',
    'goto', 'delete', 'volatile', 'synchronized', 'self', 'base', 'ref', 'out', 'mut', 'move',
    'macro', 'type', 'record', 'trait', 'impl',
)

# word -> what it is kept for
RESERVED_WORDS: Dict[str, str] = dict(_FOR_A_FEATURE)
RESERVED_WORDS.update({word: 'future use' for word in _FOR_THE_FUTURE})


def reserved_word_message(word: str) -> str:
    """The error for a reserved word used as a name."""
    return (f"'{word}' is reserved for {RESERVED_WORDS[word]} - choose another name "
            f"(after a '.' it may still be a member name)")
