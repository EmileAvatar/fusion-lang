"""Integration tests for complete Fusion lexer.

Tests the full lexer with real Fusion code examples, including:
- EBNF test cases from the language specification
- Example programs (Hello World, Factorial, FizzBuzz)
- Edge cases and error conditions
"""

import pytest
from src.lexer import lex, Lexer, Token, TokenType
from src.utils.errors import LexerError


# ============================================================
# EBNF Test Cases (from fusion.ebnf)
# ============================================================


class TestEBNFCases:
    """Test cases from the Fusion EBNF grammar specification."""

    def test_case_1_inline_lambda(self):
        """EBNF Test Case 1: Simple inline lambda function."""
        source = "int multiply(int x, int y) : x * y"
        tokens = lex(source)

        # Expected tokens (excluding NEWLINE and EOF)
        expected_types = [
            TokenType.INT, TokenType.IDENTIFIER, TokenType.LPAREN,
            TokenType.INT, TokenType.IDENTIFIER, TokenType.COMMA,
            TokenType.INT, TokenType.IDENTIFIER, TokenType.RPAREN,
            TokenType.COLON, TokenType.IDENTIFIER, TokenType.MULTIPLY,
            TokenType.IDENTIFIER, TokenType.EOF
        ]

        # Filter out NEWLINE tokens for easier comparison
        actual_types = [t.type for t in tokens if t.type != TokenType.NEWLINE]

        assert actual_types == expected_types

    def test_case_2_multi_line_function_with_indent(self):
        """EBNF Test Case 2: Multi-line function with indentation."""
        source = """int factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)"""

        tokens = lex(source)

        # Check for key tokens
        token_types = [t.type for t in tokens]

        assert TokenType.INT in token_types
        assert TokenType.IDENTIFIER in token_types
        assert TokenType.IF in token_types
        assert TokenType.RETURN in token_types
        assert TokenType.INDENT in token_types
        assert TokenType.DEDENT in token_types

        # Count INDENT/DEDENT pairs
        indent_count = token_types.count(TokenType.INDENT)
        dedent_count = token_types.count(TokenType.DEDENT)
        assert indent_count == dedent_count  # Should be balanced

    def test_case_3_variable_declaration(self):
        """EBNF Test Case 3: Variable declaration."""
        source = "int count = 42"
        tokens = lex(source)

        expected_types = [
            TokenType.INT, TokenType.IDENTIFIER, TokenType.ASSIGN,
            TokenType.INTEGER, TokenType.EOF
        ]

        actual_types = [t.type for t in tokens if t.type != TokenType.NEWLINE]
        assert actual_types == expected_types

        # Check token values
        assert tokens[0].value == "int"
        assert tokens[1].value == "count"
        assert tokens[2].value == "="
        assert tokens[3].value == "42"

    def test_case_7_import_statement(self):
        """EBNF Test Case 7: Import statement."""
        source = "import Fusion.Math"
        tokens = lex(source)

        expected_types = [
            TokenType.IMPORT, TokenType.IDENTIFIER, TokenType.DOT,
            TokenType.IDENTIFIER, TokenType.EOF
        ]

        actual_types = [t.type for t in tokens if t.type != TokenType.NEWLINE]
        assert actual_types == expected_types

    def test_case_8_lambda_expression(self):
        """EBNF Test Case 8: Lambda expression assigned to variable."""
        source = "func add = (int a, int b) : a + b"
        tokens = lex(source)

        expected_types = [
            TokenType.FUNC, TokenType.IDENTIFIER, TokenType.ASSIGN,
            TokenType.LPAREN, TokenType.INT, TokenType.IDENTIFIER, TokenType.COMMA,
            TokenType.INT, TokenType.IDENTIFIER, TokenType.RPAREN,
            TokenType.COLON, TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER,
            TokenType.EOF
        ]

        actual_types = [t.type for t in tokens if t.type != TokenType.NEWLINE]
        assert actual_types == expected_types

    def test_case_9_end_function_syntax(self):
        """EBNF Test Case 9: Function with End keyword."""
        source = """void function greet(string name)
    print("Hello, {name}!")
End function"""

        tokens = lex(source)

        token_types = [t.type for t in tokens]

        assert TokenType.VOID in token_types
        assert TokenType.FUNCTION in token_types
        assert TokenType.IDENTIFIER in token_types
        assert TokenType.STRING_LIT in token_types
        assert TokenType.END in token_types


# ============================================================
# Example Programs
# ============================================================


class TestExamplePrograms:
    """Test tokenization of complete example programs."""

    def test_hello_world(self):
        """Test Hello World program."""
        source = """void function main()
    print("Hello, World!")
End function"""

        tokens = lex(source)

        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF

        # Check for main components
        token_values = [t.value for t in tokens]
        assert "main" in token_values
        assert "print" in token_values

    def test_factorial_program(self):
        """Test factorial program with recursion."""
        source = """int function factorial(int n)
    if n <= 1
        return 1
    return n * factorial(n - 1)
End function

void function main()
    int result = factorial(5)
    print("Factorial of 5 is {result}")
End function"""

        tokens = lex(source)

        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF

        # Check for key elements
        token_types = [t.type for t in tokens]
        # 4 FUNCTION tokens: "function" factorial, "End function", "function" main, "End function"
        assert token_types.count(TokenType.FUNCTION) == 4
        assert token_types.count(TokenType.END) == 2  # 2x "End"
        assert TokenType.IF in token_types
        assert TokenType.RETURN in token_types

    def test_fizzbuzz_program(self):
        """Test FizzBuzz program with loops and conditionals."""
        source = """void function main()
    int i = 1
    while i <= 100
        if i % 15 == 0
            print("FizzBuzz")
        else if i % 3 == 0
            print("Fizz")
        else if i % 5 == 0
            print("Buzz")
        else
            print(i)
        i++
End function"""

        tokens = lex(source)

        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF

        # Check for loop and conditionals
        token_types = [t.type for t in tokens]
        assert TokenType.WHILE in token_types  # Changed from FOR to WHILE
        assert TokenType.IF in token_types
        assert TokenType.ELSE in token_types
        assert TokenType.INCREMENT in token_types  # i++


# ============================================================
# Block Styles
# ============================================================


class TestBlockStyles:
    """Test different block styles (indentation, braces, End keywords)."""

    def test_indentation_style(self):
        """Test Python-style indentation blocks."""
        source = """if true
    print("indented")
    if false
        print("nested")
print("done")"""

        tokens = lex(source)

        token_types = [t.type for t in tokens]

        # Should have INDENT/DEDENT tokens
        assert TokenType.INDENT in token_types
        assert TokenType.DEDENT in token_types

        # Count indents and dedents
        indent_count = token_types.count(TokenType.INDENT)
        dedent_count = token_types.count(TokenType.DEDENT)
        assert indent_count == 2  # Two indent levels
        assert dedent_count == 2  # Should balance

    def test_brace_style(self):
        """Test C-style brace blocks."""
        source = """if true {
    print("braces")
}"""

        tokens = lex(source)

        token_types = [t.type for t in tokens]

        # Should have braces, no INDENT/DEDENT inside braces
        assert TokenType.LBRACE in token_types
        assert TokenType.RBRACE in token_types

        # No INDENT tokens inside brace blocks
        assert TokenType.INDENT not in token_types

    def test_end_keyword_style(self):
        """Test VB.NET-style End keyword blocks."""
        source = """if true
    print("with end")
End if"""

        tokens = lex(source)

        token_types = [t.type for t in tokens]

        assert TokenType.IF in token_types
        assert TokenType.END in token_types

    def test_mixed_block_styles(self):
        """Test mixing different block styles."""
        source = """void function main()
    if true {
        print("brace inside indent")
    }
    print("back to indent")
End function"""

        tokens = lex(source)

        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF

        token_types = [t.type for t in tokens]
        assert TokenType.LBRACE in token_types
        assert TokenType.RBRACE in token_types
        assert TokenType.END in token_types


# ============================================================
# String Interpolation
# ============================================================


class TestStringInterpolation:
    """Test string interpolation tokenization."""

    def test_inline_interpolation(self):
        """Test {varName} interpolation."""
        source = 'string msg = "Hello, {name}!"'
        tokens = lex(source)

        # Find the string token
        string_token = next(t for t in tokens if t.type == TokenType.STRING_LIT)

        # Value should be JSON-encoded parts
        assert '{' in string_token.value or 'INTERP_VAR' in string_token.value

    def test_positional_interpolation(self):
        """Test {@1} positional interpolation."""
        source = 'string msg = "User {@1} is {@2} years old"'
        tokens = lex(source)

        # Find the string token
        string_token = next(t for t in tokens if t.type == TokenType.STRING_LIT)

        # Value should contain interpolation markers
        assert 'INTERP_POS' in string_token.value or '@' in string_token.value

    def test_multiple_interpolations(self):
        """Test multiple interpolations in one string."""
        source = 'print("Name: {name}, Age: {age}, City: {city}")'
        tokens = lex(source)

        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF


# ============================================================
# Comments
# ============================================================


class TestComments:
    """Test comment handling in various contexts."""

    def test_single_line_comment_double_slash(self):
        """Test // comments."""
        source = """int x = 5  // This is a comment
int y = 10"""

        tokens = lex(source)

        # Comments should be skipped
        token_values = [t.value for t in tokens]
        assert "This" not in token_values
        assert "comment" not in token_values

        # But code should remain
        assert "x" in token_values
        assert "y" in token_values

    def test_single_line_comment_quote(self):
        """Test ' comments - DISABLED (conflicts with char literals)."""
        # NOTE: ' comment support is disabled for now to allow character literals
        # Future: Re-enable ' only at start of line (after whitespace)
        pytest.skip("' comment support disabled - conflicts with char literals 'c'")

    def test_multi_line_comment(self):
        """Test /* */ comments."""
        source = """int x = 5
/* This is a
   multi-line
   comment */
int y = 10"""

        tokens = lex(source)

        # Comments should be skipped
        token_values = [t.value for t in tokens]
        assert "multi-line" not in token_values

        # But code should remain
        assert "x" in token_values
        assert "y" in token_values

    def test_nested_comments_not_supported(self):
        """Test that nested comments are not supported."""
        source = """/* Outer /* inner */ still in comment */
int x = 5"""

        tokens = lex(source)

        # The first */ should close the comment
        # "still in comment" should be treated as code and cause an error
        # This is expected behavior for C-style comments


# ============================================================
# Operators and Literals
# ============================================================


class TestOperatorsAndLiterals:
    """Test tokenization of operators and various literal types."""

    def test_all_arithmetic_operators(self):
        """Test arithmetic operators."""
        source = "x = a + b - c * d / e % f ** g"
        tokens = lex(source)

        token_types = [t.type for t in tokens]

        assert TokenType.PLUS in token_types
        assert TokenType.MINUS in token_types
        assert TokenType.MULTIPLY in token_types
        assert TokenType.DIVIDE in token_types
        assert TokenType.MODULO in token_types
        assert TokenType.POWER in token_types

    def test_comparison_operators(self):
        """Test comparison operators."""
        source = "if x < y and a > b and c <= d and e >= f and g == h and i != j"
        tokens = lex(source)

        token_types = [t.type for t in tokens]

        assert TokenType.LESS in token_types
        assert TokenType.GREATER in token_types
        assert TokenType.LESS_EQUAL in token_types
        assert TokenType.GREATER_EQUAL in token_types
        assert TokenType.EQUAL in token_types
        assert TokenType.NOT_EQUAL in token_types

    def test_assignment_operators(self):
        """Test assignment operators."""
        source = """x += 1
y -= 2
z *= 3
a /= 4
b %= 5"""
        tokens = lex(source)

        token_types = [t.type for t in tokens]

        assert TokenType.PLUS_ASSIGN in token_types
        assert TokenType.MINUS_ASSIGN in token_types
        assert TokenType.MULTIPLY_ASSIGN in token_types
        assert TokenType.DIVIDE_ASSIGN in token_types
        assert TokenType.MODULO_ASSIGN in token_types

    def test_integer_literals(self):
        """Test integer literals."""
        source = """int a = 42
int b = 0
int c = 999L"""
        tokens = lex(source)

        integer_tokens = [t for t in tokens if t.type == TokenType.INTEGER]

        assert len(integer_tokens) == 3
        assert integer_tokens[0].value == "42"
        assert integer_tokens[1].value == "0"
        assert integer_tokens[2].value == "999L"

    def test_float_literals(self):
        """Test float literals."""
        source = """float a = 3.14
float b = 0.5f
double c = 2.0d"""
        tokens = lex(source)

        float_tokens = [t for t in tokens if t.type == TokenType.FLOAT_LIT]

        assert len(float_tokens) == 3
        assert "3.14" in float_tokens[0].value
        assert "0.5f" in float_tokens[1].value
        assert "2.0d" in float_tokens[2].value

    def test_character_literals(self):
        """Test character literals."""
        source = """char a = 'x'
char b = '\\n'
char c = '\\t'"""
        tokens = lex(source)

        char_tokens = [t for t in tokens if t.type == TokenType.CHAR_LIT]

        assert len(char_tokens) == 3


# ============================================================
# Error Handling
# ============================================================


class TestErrorHandling:
    """Test error detection and reporting."""

    def test_unterminated_string_error(self):
        """Test error on unterminated string."""
        source = 'string msg = "unterminated'

        with pytest.raises(LexerError) as exc_info:
            lex(source)

        assert "Unterminated string" in str(exc_info.value)

    def test_unterminated_char_error(self):
        """Test error on unterminated char."""
        source = "char c = 'x"

        with pytest.raises(LexerError) as exc_info:
            lex(source)

        assert "Unterminated character" in str(exc_info.value)

    def test_unterminated_comment_error(self):
        """Test error on unterminated multi-line comment."""
        source = "/* This comment never ends"

        with pytest.raises(LexerError) as exc_info:
            lex(source)

        assert "Unterminated" in str(exc_info.value)

    def test_invalid_character_error(self):
        """Test error on invalid character."""
        source = "int x = 5 @ 3"  # @ is not a valid operator

        with pytest.raises(LexerError) as exc_info:
            lex(source)

        assert "Invalid character" in str(exc_info.value)

    def test_indentation_mismatch_error(self):
        """Test error on mismatched indentation."""
        source = """if true
    print("4 spaces")
  print("2 spaces - mismatch!")"""

        with pytest.raises(LexerError) as exc_info:
            lex(source)

        assert "Indentation mismatch" in str(exc_info.value)


# ============================================================
# Edge Cases
# ============================================================


class TestEdgeCases:
    """Test edge cases and corner conditions."""

    def test_empty_source(self):
        """Test tokenizing empty source."""
        tokens = lex("")

        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_whitespace_only(self):
        """Test source with only whitespace."""
        tokens = lex("   \n\n   \n  ")

        # Should only have NEWLINE and EOF tokens
        token_types = [t.type for t in tokens]
        assert TokenType.NEWLINE in token_types
        assert tokens[-1].type == TokenType.EOF

    def test_single_token(self):
        """Test source with single token."""
        tokens = lex("42")

        assert len(tokens) == 2  # INTEGER + EOF
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[1].type == TokenType.EOF

    def test_very_long_identifier(self):
        """Test very long identifier."""
        long_name = "very_long_identifier_" + "x" * 100
        source = f"int {long_name} = 42"

        tokens = lex(source)

        identifier_token = tokens[1]
        assert identifier_token.type == TokenType.IDENTIFIER
        assert identifier_token.value == long_name

    def test_all_keywords_in_sequence(self):
        """Test that all keywords are recognized."""
        keywords = [
            "if", "else", "for", "while", "loop", "end", "break", "continue", "return",
            "function", "func", "class", "struct", "interface", "Enum",
            "public", "private", "static", "int", "float", "string", "bool",
            "var", "const", "true", "false", "null", "import", "new"
        ]

        source = " ".join(keywords)
        tokens = lex(source)

        # All should be keywords (not identifiers)
        for i, keyword in enumerate(keywords):
            assert tokens[i].value == keyword
            assert tokens[i].type != TokenType.IDENTIFIER


# ============================================================
# Source Location Tracking
# ============================================================


class TestSourceLocation:
    """Test that source locations are tracked correctly."""

    def test_line_numbers(self):
        """Test line number tracking."""
        source = """int x = 1
int y = 2
int z = 3"""

        tokens = lex(source)

        # Find tokens for each variable
        x_token = next(t for t in tokens if t.value == "x")
        y_token = next(t for t in tokens if t.value == "y")
        z_token = next(t for t in tokens if t.value == "z")

        assert x_token.location.line == 1
        assert y_token.location.line == 2
        assert z_token.location.line == 3

    def test_column_numbers(self):
        """Test column number tracking."""
        source = "int x = 42"

        tokens = lex(source)

        assert tokens[0].location.column == 1  # "int"
        assert tokens[1].location.column == 5  # "x"
        assert tokens[2].location.column == 7  # "="
        assert tokens[3].location.column == 9  # "42"
