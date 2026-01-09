"""Test suite for operator tokenization.

Tests the operator lookup tables and longest-match algorithm.
"""

import pytest
from src.lexer.operators import (
    THREE_CHAR_OPERATORS,
    TWO_CHAR_OPERATORS,
    SINGLE_CHAR_OPERATORS,
    DELIMITERS,
    OPERATOR_COUNT,
    DELIMITER_COUNT,
    TOTAL_OPERATOR_AND_DELIMITER_COUNT,
    is_operator_char,
    match_operator,
    is_delimiter,
    is_operator,
)
from src.lexer.token import TokenType


class TestOperatorTables:
    """Test the operator lookup table structures."""

    def test_operator_counts(self):
        """Verify expected number of operators."""
        assert len(THREE_CHAR_OPERATORS) == 2  # ... and **=
        assert len(TWO_CHAR_OPERATORS) == 19   # All 2-char operators
        assert len(SINGLE_CHAR_OPERATORS) == 9  # Single-char operators
        assert len(DELIMITERS) == 10            # Delimiters

        assert OPERATOR_COUNT == 30  # 2 + 19 + 9
        assert DELIMITER_COUNT == 10
        assert TOTAL_OPERATOR_AND_DELIMITER_COUNT == 40

    def test_all_tables_are_dicts(self):
        """Verify all operator tables are dictionaries."""
        assert isinstance(THREE_CHAR_OPERATORS, dict)
        assert isinstance(TWO_CHAR_OPERATORS, dict)
        assert isinstance(SINGLE_CHAR_OPERATORS, dict)
        assert isinstance(DELIMITERS, dict)

    def test_all_operators_map_to_token_types(self):
        """Verify all operators map to valid TokenType values."""
        all_ops = {
            **THREE_CHAR_OPERATORS,
            **TWO_CHAR_OPERATORS,
            **SINGLE_CHAR_OPERATORS,
            **DELIMITERS
        }
        for op_str, token_type in all_ops.items():
            assert isinstance(op_str, str)
            assert isinstance(token_type, TokenType)


class TestThreeCharOperators:
    """Test 3-character operator recognition."""

    def test_range_operator(self):
        """Test ... (range) operator."""
        assert '...' in THREE_CHAR_OPERATORS
        assert THREE_CHAR_OPERATORS['...'] == TokenType.RANGE

    def test_power_assign_operator(self):
        """Test **= (power assign) operator."""
        assert '**=' in THREE_CHAR_OPERATORS
        assert THREE_CHAR_OPERATORS['**='] == TokenType.POWER_ASSIGN


class TestTwoCharOperators:
    """Test 2-character operator recognition."""

    def test_comparison_operators(self):
        """Test all 2-char comparison operators."""
        assert TWO_CHAR_OPERATORS['=='] == TokenType.EQUAL
        assert TWO_CHAR_OPERATORS['!='] == TokenType.NOT_EQUAL
        assert TWO_CHAR_OPERATORS['<>'] == TokenType.NOT_EQUAL_ALT
        assert TWO_CHAR_OPERATORS['<='] == TokenType.LESS_EQUAL
        assert TWO_CHAR_OPERATORS['>='] == TokenType.GREATER_EQUAL

    def test_logical_operators(self):
        """Test 2-char logical operators."""
        assert TWO_CHAR_OPERATORS['&&'] == TokenType.LOGICAL_AND
        assert TWO_CHAR_OPERATORS['||'] == TokenType.LOGICAL_OR

    def test_assignment_operators(self):
        """Test compound assignment operators."""
        assert TWO_CHAR_OPERATORS['+='] == TokenType.PLUS_ASSIGN
        assert TWO_CHAR_OPERATORS['-='] == TokenType.MINUS_ASSIGN
        assert TWO_CHAR_OPERATORS['*='] == TokenType.MULTIPLY_ASSIGN
        assert TWO_CHAR_OPERATORS['/='] == TokenType.DIVIDE_ASSIGN
        assert TWO_CHAR_OPERATORS['%='] == TokenType.MODULO_ASSIGN

    def test_arithmetic_operators(self):
        """Test 2-char arithmetic operators."""
        assert TWO_CHAR_OPERATORS['**'] == TokenType.POWER
        assert TWO_CHAR_OPERATORS['++'] == TokenType.INCREMENT
        assert TWO_CHAR_OPERATORS['--'] == TokenType.DECREMENT

    def test_special_operators(self):
        """Test special 2-char operators."""
        assert TWO_CHAR_OPERATORS['?.'] == TokenType.SAFE_NAV
        assert TWO_CHAR_OPERATORS['?['] == TokenType.SAFE_INDEX
        assert TWO_CHAR_OPERATORS['<-'] == TokenType.CHANNEL_SEND
        assert TWO_CHAR_OPERATORS['->'] == TokenType.ARROW


class TestSingleCharOperators:
    """Test single-character operator recognition."""

    def test_arithmetic_operators(self):
        """Test single-char arithmetic operators."""
        assert SINGLE_CHAR_OPERATORS['+'] == TokenType.PLUS
        assert SINGLE_CHAR_OPERATORS['-'] == TokenType.MINUS
        assert SINGLE_CHAR_OPERATORS['*'] == TokenType.MULTIPLY
        assert SINGLE_CHAR_OPERATORS['/'] == TokenType.DIVIDE
        assert SINGLE_CHAR_OPERATORS['%'] == TokenType.MODULO

    def test_comparison_operators(self):
        """Test single-char comparison operators."""
        assert SINGLE_CHAR_OPERATORS['<'] == TokenType.LESS
        assert SINGLE_CHAR_OPERATORS['>'] == TokenType.GREATER

    def test_assignment_operator(self):
        """Test assignment operator."""
        assert SINGLE_CHAR_OPERATORS['='] == TokenType.ASSIGN

    def test_logical_operator(self):
        """Test logical NOT operator."""
        assert SINGLE_CHAR_OPERATORS['!'] == TokenType.LOGICAL_NOT


class TestDelimiters:
    """Test delimiter recognition."""

    def test_parentheses(self):
        """Test parenthesis delimiters."""
        assert DELIMITERS['('] == TokenType.LPAREN
        assert DELIMITERS[')'] == TokenType.RPAREN

    def test_brackets(self):
        """Test bracket delimiters."""
        assert DELIMITERS['['] == TokenType.LBRACKET
        assert DELIMITERS[']'] == TokenType.RBRACKET

    def test_braces(self):
        """Test brace delimiters."""
        assert DELIMITERS['{'] == TokenType.LBRACE
        assert DELIMITERS['}'] == TokenType.RBRACE

    def test_other_delimiters(self):
        """Test other delimiters."""
        assert DELIMITERS[','] == TokenType.COMMA
        assert DELIMITERS[':'] == TokenType.COLON
        assert DELIMITERS['.'] == TokenType.DOT
        assert DELIMITERS['?'] == TokenType.QUESTION


class TestIsOperatorChar:
    """Test the is_operator_char() function."""

    def test_operator_chars(self):
        """Test that operator characters are recognized."""
        assert is_operator_char('+')
        assert is_operator_char('-')
        assert is_operator_char('*')
        assert is_operator_char('/')
        assert is_operator_char('%')
        assert is_operator_char('<')
        assert is_operator_char('>')
        assert is_operator_char('=')
        assert is_operator_char('!')
        assert is_operator_char('&')
        assert is_operator_char('|')
        assert is_operator_char('?')
        assert is_operator_char('.')
        assert is_operator_char(':')

    def test_delimiter_chars(self):
        """Test that delimiter characters are recognized."""
        assert is_operator_char('(')
        assert is_operator_char(')')
        assert is_operator_char('[')
        assert is_operator_char(']')
        assert is_operator_char('{')
        assert is_operator_char('}')
        assert is_operator_char(',')

    def test_non_operator_chars(self):
        """Test that non-operator characters are not recognized."""
        assert not is_operator_char('a')
        assert not is_operator_char('Z')
        assert not is_operator_char('0')
        assert not is_operator_char('_')
        assert not is_operator_char(' ')
        assert not is_operator_char('\n')
        assert not is_operator_char('\t')

    def test_empty_and_multi_char(self):
        """Test edge cases: empty string and multi-char."""
        assert not is_operator_char('')
        assert not is_operator_char('++')


class TestMatchOperator:
    """Test the match_operator() longest-match algorithm."""

    def test_three_char_operators(self):
        """Test 3-character operator matching."""
        result = match_operator('...', 0)
        assert result is not None
        assert result[0] == TokenType.RANGE
        assert result[1] == '...'
        assert result[2] == 3

        result = match_operator('**=', 0)
        assert result is not None
        assert result[0] == TokenType.POWER_ASSIGN
        assert result[1] == '**='
        assert result[2] == 3

    def test_two_char_operators(self):
        """Test 2-character operator matching."""
        result = match_operator('==', 0)
        assert result is not None
        assert result[0] == TokenType.EQUAL
        assert result[1] == '=='
        assert result[2] == 2

        result = match_operator('!=', 0)
        assert result is not None
        assert result[0] == TokenType.NOT_EQUAL
        assert result[1] == '!='
        assert result[2] == 2

        result = match_operator('?.', 0)
        assert result is not None
        assert result[0] == TokenType.SAFE_NAV
        assert result[1] == '?.'
        assert result[2] == 2

    def test_single_char_operators(self):
        """Test single-character operator matching."""
        result = match_operator('+', 0)
        assert result is not None
        assert result[0] == TokenType.PLUS
        assert result[1] == '+'
        assert result[2] == 1

        result = match_operator('=', 0)
        assert result is not None
        assert result[0] == TokenType.ASSIGN
        assert result[1] == '='
        assert result[2] == 1

    def test_delimiter_matching(self):
        """Test delimiter matching."""
        result = match_operator('(', 0)
        assert result is not None
        assert result[0] == TokenType.LPAREN
        assert result[1] == '('
        assert result[2] == 1

        result = match_operator('[', 0)
        assert result is not None
        assert result[0] == TokenType.LBRACKET

    def test_longest_match_priority(self):
        """Test that longest match is preferred."""
        # '...' should match as RANGE, not DOT + DOT + DOT
        result = match_operator('...', 0)
        assert result[0] == TokenType.RANGE
        assert result[2] == 3

        # '**=' should match as POWER_ASSIGN, not POWER + ASSIGN
        result = match_operator('**=', 0)
        assert result[0] == TokenType.POWER_ASSIGN
        assert result[2] == 3

        # '**' should match as POWER, not MULTIPLY + MULTIPLY
        result = match_operator('**', 0)
        assert result[0] == TokenType.POWER
        assert result[2] == 2

        # '==' should match as EQUAL, not ASSIGN + ASSIGN
        result = match_operator('==', 0)
        assert result[0] == TokenType.EQUAL
        assert result[2] == 2

    def test_match_at_different_positions(self):
        """Test matching at different positions in text."""
        text = "a + b"
        result = match_operator(text, 2)
        assert result is not None
        assert result[0] == TokenType.PLUS

        text = "x == y"
        result = match_operator(text, 2)
        assert result is not None
        assert result[0] == TokenType.EQUAL

    def test_no_match(self):
        """Test when no operator matches."""
        result = match_operator('abc', 0)
        assert result is None

        result = match_operator('123', 0)
        assert result is None

    def test_partial_text(self):
        """Test matching when text is shorter than longest operator."""
        # Only 2 chars available, should match 2-char operator
        result = match_operator('==', 0)
        assert result[0] == TokenType.EQUAL
        assert result[2] == 2

        # Only 1 char available, should match 1-char operator
        result = match_operator('+', 0)
        assert result[0] == TokenType.PLUS
        assert result[2] == 1


class TestOperatorDisambiguation:
    """Test disambiguation of similar operators."""

    def test_power_vs_multiply(self):
        """Test ** (POWER) vs * (MULTIPLY)."""
        # '**' should be POWER
        result = match_operator('**', 0)
        assert result[0] == TokenType.POWER
        assert result[2] == 2

        # '*' should be MULTIPLY
        result = match_operator('*', 0)
        assert result[0] == TokenType.MULTIPLY
        assert result[2] == 1

        # '* *' (with space) should be two MULTIPLY tokens
        result = match_operator('* *', 0)
        assert result[0] == TokenType.MULTIPLY
        assert result[2] == 1

    def test_power_assign_vs_power(self):
        """Test **= (POWER_ASSIGN) vs ** (POWER)."""
        # '**=' should be POWER_ASSIGN
        result = match_operator('**=', 0)
        assert result[0] == TokenType.POWER_ASSIGN
        assert result[2] == 3

        # '**' should be POWER
        result = match_operator('**', 0)
        assert result[0] == TokenType.POWER
        assert result[2] == 2

    def test_range_vs_dot(self):
        """Test ... (RANGE) vs . (DOT)."""
        # '...' should be RANGE
        result = match_operator('...', 0)
        assert result[0] == TokenType.RANGE
        assert result[2] == 3

        # '.' should be DOT
        result = match_operator('.', 0)
        assert result[0] == TokenType.DOT
        assert result[2] == 1

    def test_increment_vs_plus(self):
        """Test ++ (INCREMENT) vs + (PLUS)."""
        # '++' should be INCREMENT
        result = match_operator('++', 0)
        assert result[0] == TokenType.INCREMENT
        assert result[2] == 2

        # '+' should be PLUS
        result = match_operator('+', 0)
        assert result[0] == TokenType.PLUS
        assert result[2] == 1

    def test_safe_nav_vs_question_dot(self):
        """Test ?. (SAFE_NAV) vs ? and .."""
        # '?.' should be SAFE_NAV
        result = match_operator('?.', 0)
        assert result[0] == TokenType.SAFE_NAV
        assert result[2] == 2

        # '?' should be QUESTION
        result = match_operator('?', 0)
        assert result[0] == TokenType.QUESTION
        assert result[2] == 1


class TestIsDelimiter:
    """Test the is_delimiter() function."""

    def test_delimiter_types(self):
        """Test that delimiter TokenTypes are recognized."""
        assert is_delimiter(TokenType.LPAREN)
        assert is_delimiter(TokenType.RPAREN)
        assert is_delimiter(TokenType.LBRACKET)
        assert is_delimiter(TokenType.RBRACKET)
        assert is_delimiter(TokenType.LBRACE)
        assert is_delimiter(TokenType.RBRACE)
        assert is_delimiter(TokenType.COMMA)
        assert is_delimiter(TokenType.COLON)
        assert is_delimiter(TokenType.DOT)
        assert is_delimiter(TokenType.QUESTION)

    def test_non_delimiter_types(self):
        """Test that non-delimiter TokenTypes are not recognized."""
        assert not is_delimiter(TokenType.PLUS)
        assert not is_delimiter(TokenType.EQUAL)
        assert not is_delimiter(TokenType.IF)
        assert not is_delimiter(TokenType.IDENTIFIER)


class TestIsOperator:
    """Test the is_operator() function."""

    def test_operator_types(self):
        """Test that operator TokenTypes are recognized."""
        # Arithmetic
        assert is_operator(TokenType.PLUS)
        assert is_operator(TokenType.MINUS)
        assert is_operator(TokenType.MULTIPLY)
        assert is_operator(TokenType.DIVIDE)
        assert is_operator(TokenType.MODULO)
        assert is_operator(TokenType.POWER)

        # Comparison
        assert is_operator(TokenType.EQUAL)
        assert is_operator(TokenType.NOT_EQUAL)
        assert is_operator(TokenType.LESS)
        assert is_operator(TokenType.GREATER)

        # Logical
        assert is_operator(TokenType.LOGICAL_AND)
        assert is_operator(TokenType.LOGICAL_OR)
        assert is_operator(TokenType.LOGICAL_NOT)

        # Assignment
        assert is_operator(TokenType.ASSIGN)
        assert is_operator(TokenType.PLUS_ASSIGN)

        # Special
        assert is_operator(TokenType.RANGE)
        assert is_operator(TokenType.SAFE_NAV)

    def test_non_operator_types(self):
        """Test that non-operator TokenTypes are not recognized."""
        # Delimiters should not be operators
        assert not is_operator(TokenType.LPAREN)
        assert not is_operator(TokenType.COMMA)
        assert not is_operator(TokenType.DOT)

        # Keywords should not be operators
        assert not is_operator(TokenType.IF)
        assert not is_operator(TokenType.CLASS)

        # Other types
        assert not is_operator(TokenType.IDENTIFIER)
        assert not is_operator(TokenType.INTEGER)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_position(self):
        """Test matching at end of string."""
        result = match_operator('', 0)
        assert result is None

    def test_position_beyond_text(self):
        """Test position beyond text length."""
        result = match_operator('++', 5)
        assert result is None

    def test_all_three_char_operators_tested(self):
        """Ensure all 3-char operators can be matched."""
        for op in THREE_CHAR_OPERATORS.keys():
            result = match_operator(op, 0)
            assert result is not None
            assert result[1] == op
            assert result[2] == 3

    def test_all_two_char_operators_tested(self):
        """Ensure all 2-char operators can be matched."""
        for op in TWO_CHAR_OPERATORS.keys():
            result = match_operator(op, 0)
            assert result is not None
            assert result[1] == op
            assert result[2] == 2

    def test_all_single_char_operators_tested(self):
        """Ensure all 1-char operators can be matched."""
        for op in SINGLE_CHAR_OPERATORS.keys():
            result = match_operator(op, 0)
            assert result is not None
            assert result[1] == op
            assert result[2] == 1

    def test_all_delimiters_tested(self):
        """Ensure all delimiters can be matched."""
        for delim in DELIMITERS.keys():
            result = match_operator(delim, 0)
            assert result is not None
            assert result[1] == delim
            assert result[2] == 1
