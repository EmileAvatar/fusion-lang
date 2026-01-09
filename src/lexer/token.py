"""Token definitions for Fusion lexer.

This module defines the Token class, TokenType enumeration, and SourceLocation
class used by the Fusion compiler's lexical analyzer.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Set


class TokenType(Enum):
    """Enumeration of all Fusion token types.

    Includes keywords, operators, literals, delimiters, and special tokens.
    Total: 80+ distinct token types.
    """

    # ============================================================
    # KEYWORDS - Control Flow (11 tokens)
    # ============================================================
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    LOOP = auto()
    END = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    MATCH = auto()
    CASE = auto()

    # ============================================================
    # KEYWORDS - Functions (4 tokens)
    # ============================================================
    FUNCTION = auto()
    FUNC = auto()
    ASYNC = auto()
    AWAIT = auto()

    # ============================================================
    # KEYWORDS - OOP (9 tokens)
    # ============================================================
    CLASS = auto()
    STRUCT = auto()
    INTERFACE = auto()
    ENUM = auto()
    INHERITS = auto()
    IMPLEMENTS = auto()
    PROPERTY = auto()
    GET = auto()
    SET = auto()

    # ============================================================
    # KEYWORDS - Modifiers (8 tokens)
    # ============================================================
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    STATIC = auto()
    VIRTUAL = auto()
    OVERRIDE = auto()
    ABSTRACT = auto()
    SEALED = auto()

    # ============================================================
    # KEYWORDS - Types (10 tokens)
    # ============================================================
    INT = auto()
    FLOAT = auto()
    DOUBLE = auto()
    STRING = auto()
    BOOL = auto()
    CHAR = auto()
    BYTE = auto()
    SHORT = auto()
    LONG = auto()
    VOID = auto()

    # ============================================================
    # KEYWORDS - Memory (3 tokens)
    # ============================================================
    UNIQUE = auto()
    SHARED = auto()
    WEAK = auto()

    # ============================================================
    # KEYWORDS - Variables (2 tokens)
    # ============================================================
    VAR = auto()
    CONST = auto()

    # ============================================================
    # KEYWORDS - Literals (4 tokens)
    # ============================================================
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    THIS = auto()

    # ============================================================
    # KEYWORDS - Operators (word-based) (5 tokens)
    # ============================================================
    AND = auto()
    OR = auto()
    NOT = auto()
    IS = auto()
    IN = auto()

    # ============================================================
    # KEYWORDS - Other (9 tokens)
    # ============================================================
    IMPORT = auto()
    NEW = auto()
    CAST = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    ERROR = auto()
    GO = auto()

    # ============================================================
    # OPERATORS - Arithmetic (6 tokens)
    # ============================================================
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # **

    # ============================================================
    # OPERATORS - Comparison (7 tokens)
    # ============================================================
    LESS = auto()           # <
    GREATER = auto()        # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    NOT_EQUAL_ALT = auto()  # <> (alternative syntax)

    # ============================================================
    # OPERATORS - Logical (3 tokens)
    # ============================================================
    LOGICAL_AND = auto()    # &&
    LOGICAL_OR = auto()     # ||
    LOGICAL_NOT = auto()    # !

    # ============================================================
    # OPERATORS - Assignment (7 tokens)
    # ============================================================
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    MULTIPLY_ASSIGN = auto()  # *=
    DIVIDE_ASSIGN = auto()  # /=
    MODULO_ASSIGN = auto()  # %=
    POWER_ASSIGN = auto()   # **=

    # ============================================================
    # OPERATORS - Special (7 tokens)
    # ============================================================
    RANGE = auto()          # ...
    SAFE_NAV = auto()       # ?.
    SAFE_INDEX = auto()     # ?[
    CHANNEL_SEND = auto()   # <-
    ARROW = auto()          # ->
    INCREMENT = auto()      # ++
    DECREMENT = auto()      # --

    # ============================================================
    # DELIMITERS (10 tokens)
    # ============================================================
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    COMMA = auto()          # ,
    COLON = auto()          # :
    DOT = auto()            # .
    QUESTION = auto()       # ?

    # ============================================================
    # LITERALS (4 tokens)
    # ============================================================
    INTEGER = auto()        # 42, 0x1A, 0b1010
    FLOAT_LIT = auto()      # 3.14, 2.0, 1e-5
    STRING_LIT = auto()     # "hello", 'world'
    CHAR_LIT = auto()       # 'a', '\n'

    # ============================================================
    # IDENTIFIERS (1 token)
    # ============================================================
    IDENTIFIER = auto()     # variable names, function names

    # ============================================================
    # SPECIAL TOKENS (4 tokens)
    # ============================================================
    INDENT = auto()         # Indentation increase
    DEDENT = auto()         # Indentation decrease
    NEWLINE = auto()        # Newline character
    EOF = auto()            # End of file


# Build keyword sets for quick lookups
_KEYWORD_TYPES: Set[TokenType] = {
    # Control Flow
    TokenType.IF, TokenType.ELSE, TokenType.FOR, TokenType.WHILE,
    TokenType.LOOP, TokenType.END, TokenType.BREAK, TokenType.CONTINUE,
    TokenType.RETURN, TokenType.MATCH, TokenType.CASE,

    # Functions
    TokenType.FUNCTION, TokenType.FUNC, TokenType.ASYNC, TokenType.AWAIT,

    # OOP
    TokenType.CLASS, TokenType.STRUCT, TokenType.INTERFACE, TokenType.ENUM,
    TokenType.INHERITS, TokenType.IMPLEMENTS, TokenType.PROPERTY,
    TokenType.GET, TokenType.SET,

    # Modifiers
    TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED, TokenType.STATIC,
    TokenType.VIRTUAL, TokenType.OVERRIDE, TokenType.ABSTRACT, TokenType.SEALED,

    # Types
    TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE, TokenType.STRING,
    TokenType.BOOL, TokenType.CHAR, TokenType.BYTE, TokenType.SHORT,
    TokenType.LONG, TokenType.VOID,

    # Memory
    TokenType.UNIQUE, TokenType.SHARED, TokenType.WEAK,

    # Variables
    TokenType.VAR, TokenType.CONST,

    # Literals
    TokenType.TRUE, TokenType.FALSE, TokenType.NULL, TokenType.THIS,

    # Operators (word-based)
    TokenType.AND, TokenType.OR, TokenType.NOT, TokenType.IS, TokenType.IN,

    # Other
    TokenType.IMPORT, TokenType.NEW, TokenType.CAST, TokenType.TRY,
    TokenType.CATCH, TokenType.FINALLY, TokenType.THROW, TokenType.ERROR,
    TokenType.GO,
}

_OPERATOR_TYPES: Set[TokenType] = {
    # Arithmetic
    TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
    TokenType.MODULO, TokenType.POWER,

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
    TokenType.CHANNEL_SEND, TokenType.ARROW, TokenType.INCREMENT,
    TokenType.DECREMENT,
}


@dataclass(frozen=True)
class SourceLocation:
    """Represents a location in source code for error reporting.

    Attributes:
        filename: Name of the source file
        line: Line number (1-based)
        column: Column number (1-based)
    """
    filename: str
    line: int
    column: int

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.filename}:{self.line}:{self.column}"

    def to_string(self) -> str:
        """Format as file:line:col for error messages.

        Returns:
            Formatted string like "example.fusion:42:15"
        """
        return f"{self.filename}:{self.line}:{self.column}"


@dataclass(frozen=True)
class Token:
    """Represents a single token from the lexer.

    Tokens are immutable (frozen dataclass) to prevent accidental modification
    and to allow use as dictionary keys.

    Attributes:
        type: The type of token (from TokenType enum)
        value: The original text value from source code
        location: Source code location for error reporting
    """
    type: TokenType
    value: str
    location: SourceLocation

    def __repr__(self) -> str:
        """String representation for debugging.

        Returns:
            String like "Token(IF, 'if', example.fusion:5:10)"
        """
        return f"Token({self.type.name}, '{self.value}', {self.location})"

    def is_keyword(self) -> bool:
        """Check if this token is a keyword.

        Returns:
            True if token is any Fusion keyword, False otherwise
        """
        return self.type in _KEYWORD_TYPES

    def is_operator(self) -> bool:
        """Check if this token is an operator.

        Returns:
            True if token is any operator (arithmetic, comparison, etc.)
        """
        return self.type in _OPERATOR_TYPES

    def is_literal(self) -> bool:
        """Check if this token is a literal value.

        Returns:
            True if token is integer, float, string, or char literal
        """
        return self.type in {
            TokenType.INTEGER, TokenType.FLOAT_LIT,
            TokenType.STRING_LIT, TokenType.CHAR_LIT,
            TokenType.TRUE, TokenType.FALSE, TokenType.NULL
        }

    def is_delimiter(self) -> bool:
        """Check if this token is a delimiter.

        Returns:
            True if token is parenthesis, bracket, brace, comma, etc.
        """
        return self.type in {
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACKET,
            TokenType.RBRACKET, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.COMMA, TokenType.COLON, TokenType.DOT, TokenType.QUESTION
        }
