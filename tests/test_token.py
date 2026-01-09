"""Unit tests for Token, TokenType, and SourceLocation classes.

Tests the foundational token infrastructure for the Fusion lexer.
"""

import pytest
from src.lexer.token import Token, TokenType, SourceLocation


# ============================================================
# SourceLocation Tests
# ============================================================

def test_source_location_creation():
    """Test basic SourceLocation creation."""
    loc = SourceLocation("test.fusion", 10, 5)

    assert loc.filename == "test.fusion"
    assert loc.line == 10
    assert loc.column == 5


def test_source_location_repr():
    """Test SourceLocation string representation."""
    loc = SourceLocation("example.fusion", 42, 15)

    assert repr(loc) == "example.fusion:42:15"
    assert str(loc) == "example.fusion:42:15"


def test_source_location_to_string():
    """Test SourceLocation to_string method."""
    loc = SourceLocation("test.fusion", 5, 10)

    assert loc.to_string() == "test.fusion:5:10"


def test_source_location_equality():
    """Test SourceLocation equality comparison."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 1, 1)
    loc3 = SourceLocation("test.fusion", 2, 1)

    assert loc1 == loc2
    assert loc1 != loc3


def test_source_location_immutability():
    """Test that SourceLocation is immutable."""
    loc = SourceLocation("test.fusion", 1, 1)

    with pytest.raises(AttributeError):
        loc.line = 5  # Should raise error (frozen dataclass)


# ============================================================
# Token Tests
# ============================================================

def test_token_creation():
    """Test basic Token creation."""
    loc = SourceLocation("test.fusion", 1, 1)
    token = Token(TokenType.INTEGER, "42", loc)

    assert token.type == TokenType.INTEGER
    assert token.value == "42"
    assert token.location == loc


def test_token_equality():
    """Test Token equality comparison."""
    loc1 = SourceLocation("test.fusion", 1, 1)
    loc2 = SourceLocation("test.fusion", 1, 1)

    token1 = Token(TokenType.INTEGER, "42", loc1)
    token2 = Token(TokenType.INTEGER, "42", loc2)
    token3 = Token(TokenType.FLOAT_LIT, "42.0", loc1)

    assert token1 == token2
    assert token1 != token3


def test_token_repr():
    """Test Token string representation."""
    loc = SourceLocation("test.fusion", 5, 10)
    token = Token(TokenType.IF, "if", loc)

    repr_str = repr(token)
    assert "IF" in repr_str
    assert "'if'" in repr_str
    assert "5:10" in repr_str


def test_token_immutability():
    """Test that Tokens are immutable."""
    loc = SourceLocation("test.fusion", 1, 1)
    token = Token(TokenType.INTEGER, "42", loc)

    with pytest.raises(AttributeError):
        token.type = TokenType.FLOAT_LIT  # Should raise error (frozen)


# ============================================================
# TokenType Enum Tests
# ============================================================

def test_token_type_control_flow_keywords():
    """Test control flow keyword tokens exist."""
    assert hasattr(TokenType, 'IF')
    assert hasattr(TokenType, 'ELSE')
    assert hasattr(TokenType, 'FOR')
    assert hasattr(TokenType, 'WHILE')
    assert hasattr(TokenType, 'LOOP')
    assert hasattr(TokenType, 'END')
    assert hasattr(TokenType, 'BREAK')
    assert hasattr(TokenType, 'CONTINUE')
    assert hasattr(TokenType, 'RETURN')
    assert hasattr(TokenType, 'MATCH')
    assert hasattr(TokenType, 'CASE')


def test_token_type_function_keywords():
    """Test function-related keyword tokens exist."""
    assert hasattr(TokenType, 'FUNCTION')
    assert hasattr(TokenType, 'FUNC')
    assert hasattr(TokenType, 'ASYNC')
    assert hasattr(TokenType, 'AWAIT')


def test_token_type_oop_keywords():
    """Test OOP keyword tokens exist."""
    assert hasattr(TokenType, 'CLASS')
    assert hasattr(TokenType, 'STRUCT')
    assert hasattr(TokenType, 'INTERFACE')
    assert hasattr(TokenType, 'ENUM')
    assert hasattr(TokenType, 'INHERITS')
    assert hasattr(TokenType, 'IMPLEMENTS')
    assert hasattr(TokenType, 'PROPERTY')
    assert hasattr(TokenType, 'GET')
    assert hasattr(TokenType, 'SET')


def test_token_type_modifier_keywords():
    """Test modifier keyword tokens exist."""
    assert hasattr(TokenType, 'PUBLIC')
    assert hasattr(TokenType, 'PRIVATE')
    assert hasattr(TokenType, 'PROTECTED')
    assert hasattr(TokenType, 'STATIC')
    assert hasattr(TokenType, 'VIRTUAL')
    assert hasattr(TokenType, 'OVERRIDE')
    assert hasattr(TokenType, 'ABSTRACT')
    assert hasattr(TokenType, 'SEALED')


def test_token_type_type_keywords():
    """Test type keyword tokens exist."""
    assert hasattr(TokenType, 'INT')
    assert hasattr(TokenType, 'FLOAT')
    assert hasattr(TokenType, 'DOUBLE')
    assert hasattr(TokenType, 'STRING')
    assert hasattr(TokenType, 'BOOL')
    assert hasattr(TokenType, 'CHAR')
    assert hasattr(TokenType, 'BYTE')
    assert hasattr(TokenType, 'SHORT')
    assert hasattr(TokenType, 'LONG')
    assert hasattr(TokenType, 'VOID')


def test_token_type_memory_keywords():
    """Test memory-related keyword tokens exist."""
    assert hasattr(TokenType, 'UNIQUE')
    assert hasattr(TokenType, 'SHARED')
    assert hasattr(TokenType, 'WEAK')


def test_token_type_variable_keywords():
    """Test variable keyword tokens exist."""
    assert hasattr(TokenType, 'VAR')
    assert hasattr(TokenType, 'CONST')


def test_token_type_literal_keywords():
    """Test literal keyword tokens exist."""
    assert hasattr(TokenType, 'TRUE')
    assert hasattr(TokenType, 'FALSE')
    assert hasattr(TokenType, 'NULL')
    assert hasattr(TokenType, 'THIS')


def test_token_type_operator_keywords():
    """Test operator keyword tokens exist."""
    assert hasattr(TokenType, 'AND')
    assert hasattr(TokenType, 'OR')
    assert hasattr(TokenType, 'NOT')
    assert hasattr(TokenType, 'IS')
    assert hasattr(TokenType, 'IN')


def test_token_type_other_keywords():
    """Test other keyword tokens exist."""
    assert hasattr(TokenType, 'IMPORT')
    assert hasattr(TokenType, 'NEW')
    assert hasattr(TokenType, 'CAST')
    assert hasattr(TokenType, 'TRY')
    assert hasattr(TokenType, 'CATCH')
    assert hasattr(TokenType, 'FINALLY')
    assert hasattr(TokenType, 'THROW')
    assert hasattr(TokenType, 'ERROR')
    assert hasattr(TokenType, 'GO')


def test_token_type_arithmetic_operators():
    """Test arithmetic operator tokens exist."""
    assert hasattr(TokenType, 'PLUS')
    assert hasattr(TokenType, 'MINUS')
    assert hasattr(TokenType, 'MULTIPLY')
    assert hasattr(TokenType, 'DIVIDE')
    assert hasattr(TokenType, 'MODULO')
    assert hasattr(TokenType, 'POWER')


def test_token_type_comparison_operators():
    """Test comparison operator tokens exist."""
    assert hasattr(TokenType, 'LESS')
    assert hasattr(TokenType, 'GREATER')
    assert hasattr(TokenType, 'LESS_EQUAL')
    assert hasattr(TokenType, 'GREATER_EQUAL')
    assert hasattr(TokenType, 'EQUAL')
    assert hasattr(TokenType, 'NOT_EQUAL')
    assert hasattr(TokenType, 'NOT_EQUAL_ALT')


def test_token_type_logical_operators():
    """Test logical operator tokens exist."""
    assert hasattr(TokenType, 'LOGICAL_AND')
    assert hasattr(TokenType, 'LOGICAL_OR')
    assert hasattr(TokenType, 'LOGICAL_NOT')


def test_token_type_assignment_operators():
    """Test assignment operator tokens exist."""
    assert hasattr(TokenType, 'ASSIGN')
    assert hasattr(TokenType, 'PLUS_ASSIGN')
    assert hasattr(TokenType, 'MINUS_ASSIGN')
    assert hasattr(TokenType, 'MULTIPLY_ASSIGN')
    assert hasattr(TokenType, 'DIVIDE_ASSIGN')
    assert hasattr(TokenType, 'MODULO_ASSIGN')
    assert hasattr(TokenType, 'POWER_ASSIGN')


def test_token_type_special_operators():
    """Test special operator tokens exist."""
    assert hasattr(TokenType, 'RANGE')
    assert hasattr(TokenType, 'SAFE_NAV')
    assert hasattr(TokenType, 'SAFE_INDEX')
    assert hasattr(TokenType, 'CHANNEL_SEND')
    assert hasattr(TokenType, 'ARROW')
    assert hasattr(TokenType, 'INCREMENT')
    assert hasattr(TokenType, 'DECREMENT')


def test_token_type_delimiters():
    """Test delimiter tokens exist."""
    assert hasattr(TokenType, 'LPAREN')
    assert hasattr(TokenType, 'RPAREN')
    assert hasattr(TokenType, 'LBRACKET')
    assert hasattr(TokenType, 'RBRACKET')
    assert hasattr(TokenType, 'LBRACE')
    assert hasattr(TokenType, 'RBRACE')
    assert hasattr(TokenType, 'COMMA')
    assert hasattr(TokenType, 'COLON')
    assert hasattr(TokenType, 'DOT')
    assert hasattr(TokenType, 'QUESTION')


def test_token_type_literals():
    """Test literal tokens exist."""
    assert hasattr(TokenType, 'INTEGER')
    assert hasattr(TokenType, 'FLOAT_LIT')
    assert hasattr(TokenType, 'STRING_LIT')
    assert hasattr(TokenType, 'CHAR_LIT')


def test_token_type_identifier():
    """Test identifier token exists."""
    assert hasattr(TokenType, 'IDENTIFIER')


def test_token_type_special_tokens():
    """Test special tokens exist."""
    assert hasattr(TokenType, 'INDENT')
    assert hasattr(TokenType, 'DEDENT')
    assert hasattr(TokenType, 'NEWLINE')
    assert hasattr(TokenType, 'EOF')


# ============================================================
# Token Helper Method Tests
# ============================================================

def test_is_keyword():
    """Test is_keyword helper method."""
    loc = SourceLocation("test.fusion", 1, 1)

    # Keywords should return True
    assert Token(TokenType.IF, "if", loc).is_keyword()
    assert Token(TokenType.CLASS, "class", loc).is_keyword()
    assert Token(TokenType.RETURN, "return", loc).is_keyword()
    assert Token(TokenType.INT, "int", loc).is_keyword()
    assert Token(TokenType.TRUE, "true", loc).is_keyword()

    # Non-keywords should return False
    assert not Token(TokenType.IDENTIFIER, "myVar", loc).is_keyword()
    assert not Token(TokenType.INTEGER, "42", loc).is_keyword()
    assert not Token(TokenType.PLUS, "+", loc).is_keyword()


def test_is_operator():
    """Test is_operator helper method."""
    loc = SourceLocation("test.fusion", 1, 1)

    # Operators should return True
    assert Token(TokenType.PLUS, "+", loc).is_operator()
    assert Token(TokenType.EQUAL, "==", loc).is_operator()
    assert Token(TokenType.LOGICAL_AND, "&&", loc).is_operator()
    assert Token(TokenType.ASSIGN, "=", loc).is_operator()
    assert Token(TokenType.RANGE, "...", loc).is_operator()

    # Non-operators should return False
    assert not Token(TokenType.IF, "if", loc).is_operator()
    assert not Token(TokenType.IDENTIFIER, "x", loc).is_operator()
    assert not Token(TokenType.INTEGER, "42", loc).is_operator()


def test_is_literal():
    """Test is_literal helper method."""
    loc = SourceLocation("test.fusion", 1, 1)

    # Literals should return True
    assert Token(TokenType.INTEGER, "42", loc).is_literal()
    assert Token(TokenType.FLOAT_LIT, "3.14", loc).is_literal()
    assert Token(TokenType.STRING_LIT, "hello", loc).is_literal()
    assert Token(TokenType.CHAR_LIT, "a", loc).is_literal()
    assert Token(TokenType.TRUE, "true", loc).is_literal()
    assert Token(TokenType.FALSE, "false", loc).is_literal()
    assert Token(TokenType.NULL, "null", loc).is_literal()

    # Non-literals should return False
    assert not Token(TokenType.IDENTIFIER, "x", loc).is_literal()
    assert not Token(TokenType.IF, "if", loc).is_literal()
    assert not Token(TokenType.PLUS, "+", loc).is_literal()


def test_is_delimiter():
    """Test is_delimiter helper method."""
    loc = SourceLocation("test.fusion", 1, 1)

    # Delimiters should return True
    assert Token(TokenType.LPAREN, "(", loc).is_delimiter()
    assert Token(TokenType.RPAREN, ")", loc).is_delimiter()
    assert Token(TokenType.LBRACE, "{", loc).is_delimiter()
    assert Token(TokenType.COMMA, ",", loc).is_delimiter()
    assert Token(TokenType.COLON, ":", loc).is_delimiter()

    # Non-delimiters should return False
    assert not Token(TokenType.IF, "if", loc).is_delimiter()
    assert not Token(TokenType.PLUS, "+", loc).is_delimiter()
    assert not Token(TokenType.INTEGER, "42", loc).is_delimiter()


# ============================================================
# Edge Case Tests
# ============================================================

def test_token_with_empty_value():
    """Test token with empty string value."""
    loc = SourceLocation("test.fusion", 1, 1)
    token = Token(TokenType.NEWLINE, "", loc)

    assert token.value == ""
    assert token.type == TokenType.NEWLINE


def test_token_with_multiline_location():
    """Test token spanning multiple lines."""
    loc = SourceLocation("test.fusion", 100, 1)
    token = Token(TokenType.STRING_LIT, "multi\nline\nstring", loc)

    assert token.location.line == 100
    assert "\n" in token.value


def test_source_location_with_zero_line():
    """Test SourceLocation with line 0 (edge case)."""
    loc = SourceLocation("test.fusion", 0, 0)

    assert loc.line == 0
    assert loc.column == 0


def test_token_type_uniqueness():
    """Test that all TokenType values are unique."""
    token_values = [member.value for member in TokenType]
    assert len(token_values) == len(set(token_values))


def test_token_type_count():
    """Test that we have at least 80+ token types."""
    token_count = len(TokenType)
    assert token_count >= 80, f"Expected at least 80 token types, got {token_count}"
