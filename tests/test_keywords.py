"""Test suite for keyword recognition.

Tests the keyword lookup table and keyword vs identifier distinction.
"""

import pytest
from src.lexer.keywords import (
    KEYWORDS,
    KEYWORD_COUNT,
    is_keyword,
    get_keyword_type,
)
from src.lexer.token import TokenType


class TestKeywordTable:
    """Test the keyword lookup table structure."""

    def test_keyword_count(self):
        """Verify expected number of keywords."""
        # 67 keywords total (including special cases: 'Enum'/'enum', 'End'/'end')
        assert KEYWORD_COUNT == 67
        assert len(KEYWORDS) == 67

    def test_keyword_table_is_dict(self):
        """Verify KEYWORDS is a dictionary."""
        assert isinstance(KEYWORDS, dict)

    def test_all_keywords_map_to_token_types(self):
        """Verify all keywords map to valid TokenType values."""
        for keyword, token_type in KEYWORDS.items():
            assert isinstance(keyword, str)
            assert isinstance(token_type, TokenType)


class TestControlFlowKeywords:
    """Test control flow keyword recognition."""

    def test_if_keyword(self):
        assert is_keyword('if')
        assert get_keyword_type('if') == TokenType.IF

    def test_else_keyword(self):
        assert is_keyword('else')
        assert get_keyword_type('else') == TokenType.ELSE

    def test_for_keyword(self):
        assert is_keyword('for')
        assert get_keyword_type('for') == TokenType.FOR

    def test_while_keyword(self):
        assert is_keyword('while')
        assert get_keyword_type('while') == TokenType.WHILE

    def test_loop_keyword(self):
        assert is_keyword('loop')
        assert get_keyword_type('loop') == TokenType.LOOP

    def test_end_keyword(self):
        assert is_keyword('end')
        assert get_keyword_type('end') == TokenType.END

    def test_break_keyword(self):
        assert is_keyword('break')
        assert get_keyword_type('break') == TokenType.BREAK

    def test_continue_keyword(self):
        assert is_keyword('continue')
        assert get_keyword_type('continue') == TokenType.CONTINUE

    def test_return_keyword(self):
        assert is_keyword('return')
        assert get_keyword_type('return') == TokenType.RETURN

    def test_match_keyword(self):
        assert is_keyword('match')
        assert get_keyword_type('match') == TokenType.MATCH

    def test_case_keyword(self):
        assert is_keyword('case')
        assert get_keyword_type('case') == TokenType.CASE


class TestFunctionKeywords:
    """Test function-related keyword recognition."""

    def test_function_keyword(self):
        assert is_keyword('function')
        assert get_keyword_type('function') == TokenType.FUNCTION

    def test_func_keyword(self):
        assert is_keyword('func')
        assert get_keyword_type('func') == TokenType.FUNC

    def test_async_keyword(self):
        assert is_keyword('async')
        assert get_keyword_type('async') == TokenType.ASYNC

    def test_await_keyword(self):
        assert is_keyword('await')
        assert get_keyword_type('await') == TokenType.AWAIT


class TestOOPKeywords:
    """Test OOP-related keyword recognition."""

    def test_class_keyword(self):
        assert is_keyword('class')
        assert get_keyword_type('class') == TokenType.CLASS

    def test_struct_keyword(self):
        assert is_keyword('struct')
        assert get_keyword_type('struct') == TokenType.STRUCT

    def test_interface_keyword(self):
        assert is_keyword('interface')
        assert get_keyword_type('interface') == TokenType.INTERFACE

    def test_enum_lowercase(self):
        assert is_keyword('enum')
        assert get_keyword_type('enum') == TokenType.ENUM

    def test_enum_capitalized(self):
        """Special case: Enum with capital E is allowed."""
        assert is_keyword('Enum')
        assert get_keyword_type('Enum') == TokenType.ENUM

    def test_inherits_keyword(self):
        assert is_keyword('inherits')
        assert get_keyword_type('inherits') == TokenType.INHERITS

    def test_implements_keyword(self):
        assert is_keyword('implements')
        assert get_keyword_type('implements') == TokenType.IMPLEMENTS

    def test_property_keyword(self):
        assert is_keyword('property')
        assert get_keyword_type('property') == TokenType.PROPERTY

    def test_get_keyword(self):
        assert is_keyword('get')
        assert get_keyword_type('get') == TokenType.GET

    def test_set_keyword(self):
        assert is_keyword('set')
        assert get_keyword_type('set') == TokenType.SET


class TestModifierKeywords:
    """Test modifier keyword recognition."""

    def test_public_keyword(self):
        assert is_keyword('public')
        assert get_keyword_type('public') == TokenType.PUBLIC

    def test_private_keyword(self):
        assert is_keyword('private')
        assert get_keyword_type('private') == TokenType.PRIVATE

    def test_protected_keyword(self):
        assert is_keyword('protected')
        assert get_keyword_type('protected') == TokenType.PROTECTED

    def test_static_keyword(self):
        assert is_keyword('static')
        assert get_keyword_type('static') == TokenType.STATIC

    def test_virtual_keyword(self):
        assert is_keyword('virtual')
        assert get_keyword_type('virtual') == TokenType.VIRTUAL

    def test_override_keyword(self):
        assert is_keyword('override')
        assert get_keyword_type('override') == TokenType.OVERRIDE

    def test_abstract_keyword(self):
        assert is_keyword('abstract')
        assert get_keyword_type('abstract') == TokenType.ABSTRACT

    def test_sealed_keyword(self):
        assert is_keyword('sealed')
        assert get_keyword_type('sealed') == TokenType.SEALED


class TestTypeKeywords:
    """Test type keyword recognition."""

    def test_int_keyword(self):
        assert is_keyword('int')
        assert get_keyword_type('int') == TokenType.INT

    def test_float_keyword(self):
        assert is_keyword('float')
        assert get_keyword_type('float') == TokenType.FLOAT

    def test_double_keyword(self):
        assert is_keyword('double')
        assert get_keyword_type('double') == TokenType.DOUBLE

    def test_string_keyword(self):
        assert is_keyword('string')
        assert get_keyword_type('string') == TokenType.STRING

    def test_bool_keyword(self):
        assert is_keyword('bool')
        assert get_keyword_type('bool') == TokenType.BOOL

    def test_char_keyword(self):
        assert is_keyword('char')
        assert get_keyword_type('char') == TokenType.CHAR

    def test_byte_keyword(self):
        assert is_keyword('byte')
        assert get_keyword_type('byte') == TokenType.BYTE

    def test_short_keyword(self):
        assert is_keyword('short')
        assert get_keyword_type('short') == TokenType.SHORT

    def test_long_keyword(self):
        assert is_keyword('long')
        assert get_keyword_type('long') == TokenType.LONG

    def test_void_keyword(self):
        assert is_keyword('void')
        assert get_keyword_type('void') == TokenType.VOID


class TestMemoryKeywords:
    """Test memory management keyword recognition."""

    def test_unique_capitalized(self):
        """Unique requires capital U."""
        assert is_keyword('Unique')
        assert get_keyword_type('Unique') == TokenType.UNIQUE

    def test_shared_capitalized(self):
        """Shared requires capital S."""
        assert is_keyword('Shared')
        assert get_keyword_type('Shared') == TokenType.SHARED

    def test_weak_capitalized(self):
        """Weak requires capital W."""
        assert is_keyword('Weak')
        assert get_keyword_type('Weak') == TokenType.WEAK

    def test_lowercase_memory_not_keywords(self):
        """Lowercase memory keywords should be identifiers."""
        assert not is_keyword('unique')
        assert not is_keyword('shared')
        assert not is_keyword('weak')
        assert get_keyword_type('unique') == TokenType.IDENTIFIER
        assert get_keyword_type('shared') == TokenType.IDENTIFIER
        assert get_keyword_type('weak') == TokenType.IDENTIFIER


class TestVariableKeywords:
    """Test variable declaration keyword recognition."""

    def test_var_keyword(self):
        assert is_keyword('var')
        assert get_keyword_type('var') == TokenType.VAR

    def test_const_keyword(self):
        assert is_keyword('const')
        assert get_keyword_type('const') == TokenType.CONST


class TestLiteralKeywords:
    """Test literal keyword recognition."""

    def test_true_keyword(self):
        assert is_keyword('true')
        assert get_keyword_type('true') == TokenType.TRUE

    def test_false_keyword(self):
        assert is_keyword('false')
        assert get_keyword_type('false') == TokenType.FALSE

    def test_null_keyword(self):
        assert is_keyword('null')
        assert get_keyword_type('null') == TokenType.NULL

    def test_this_keyword(self):
        assert is_keyword('this')
        assert get_keyword_type('this') == TokenType.THIS


class TestOperatorKeywords:
    """Test word-based operator keyword recognition."""

    def test_and_keyword(self):
        assert is_keyword('and')
        assert get_keyword_type('and') == TokenType.AND

    def test_or_keyword(self):
        assert is_keyword('or')
        assert get_keyword_type('or') == TokenType.OR

    def test_not_keyword(self):
        assert is_keyword('not')
        assert get_keyword_type('not') == TokenType.NOT

    def test_is_keyword(self):
        assert is_keyword('is')
        assert get_keyword_type('is') == TokenType.IS

    def test_in_keyword(self):
        assert is_keyword('in')
        assert get_keyword_type('in') == TokenType.IN


class TestOtherKeywords:
    """Test miscellaneous keyword recognition."""

    def test_import_keyword(self):
        assert is_keyword('import')
        assert get_keyword_type('import') == TokenType.IMPORT

    def test_new_keyword(self):
        assert is_keyword('new')
        assert get_keyword_type('new') == TokenType.NEW

    def test_cast_keyword(self):
        assert is_keyword('cast')
        assert get_keyword_type('cast') == TokenType.CAST

    def test_try_keyword(self):
        assert is_keyword('try')
        assert get_keyword_type('try') == TokenType.TRY

    def test_catch_keyword(self):
        assert is_keyword('catch')
        assert get_keyword_type('catch') == TokenType.CATCH

    def test_finally_keyword(self):
        assert is_keyword('finally')
        assert get_keyword_type('finally') == TokenType.FINALLY

    def test_throw_keyword(self):
        assert is_keyword('throw')
        assert get_keyword_type('throw') == TokenType.THROW

    def test_error_capitalized(self):
        """Error requires capital E."""
        assert is_keyword('Error')
        assert get_keyword_type('Error') == TokenType.ERROR

    def test_go_keyword(self):
        assert is_keyword('go')
        assert get_keyword_type('go') == TokenType.GO


class TestCaseSensitivity:
    """Test case sensitivity of keyword recognition."""

    def test_keywords_are_case_sensitive(self):
        """Keywords must match exact case."""
        # Lowercase keywords
        assert is_keyword('if')
        assert not is_keyword('IF')
        assert not is_keyword('If')

        assert is_keyword('class')
        assert not is_keyword('CLASS')
        assert not is_keyword('Class')

        assert is_keyword('int')
        assert not is_keyword('INT')
        assert not is_keyword('Int')

    def test_capitalized_keywords(self):
        """Some keywords require capital letters."""
        # Memory keywords require capitals
        assert is_keyword('Unique')
        assert not is_keyword('unique')

        assert is_keyword('Shared')
        assert not is_keyword('shared')

        assert is_keyword('Weak')
        assert not is_keyword('weak')

        # Error requires capital E
        assert is_keyword('Error')
        assert not is_keyword('error')

        # Enum allows both
        assert is_keyword('Enum')
        assert is_keyword('enum')

    def test_all_caps_are_identifiers(self):
        """All caps versions of keywords are identifiers."""
        assert get_keyword_type('IF') == TokenType.IDENTIFIER
        assert get_keyword_type('CLASS') == TokenType.IDENTIFIER
        assert get_keyword_type('INT') == TokenType.IDENTIFIER
        assert get_keyword_type('STRING') == TokenType.IDENTIFIER
        assert get_keyword_type('WHILE') == TokenType.IDENTIFIER


class TestIdentifierRecognition:
    """Test that non-keywords are recognized as identifiers."""

    def test_simple_identifiers(self):
        """Common variable names should be identifiers."""
        assert not is_keyword('myVariable')
        assert not is_keyword('userName')
        assert not is_keyword('totalCount')
        assert not is_keyword('calculate')

        assert get_keyword_type('myVariable') == TokenType.IDENTIFIER
        assert get_keyword_type('userName') == TokenType.IDENTIFIER
        assert get_keyword_type('totalCount') == TokenType.IDENTIFIER
        assert get_keyword_type('calculate') == TokenType.IDENTIFIER

    def test_keyword_like_identifiers(self):
        """Identifiers that resemble keywords."""
        assert not is_keyword('ifCondition')
        assert not is_keyword('forLoop')
        assert not is_keyword('className')
        assert not is_keyword('intValue')

        assert get_keyword_type('ifCondition') == TokenType.IDENTIFIER
        assert get_keyword_type('forLoop') == TokenType.IDENTIFIER
        assert get_keyword_type('className') == TokenType.IDENTIFIER
        assert get_keyword_type('intValue') == TokenType.IDENTIFIER

    def test_underscored_identifiers(self):
        """Identifiers with underscores."""
        assert not is_keyword('my_variable')
        assert not is_keyword('_private')
        assert not is_keyword('__init__')

        assert get_keyword_type('my_variable') == TokenType.IDENTIFIER
        assert get_keyword_type('_private') == TokenType.IDENTIFIER
        assert get_keyword_type('__init__') == TokenType.IDENTIFIER

    def test_mixed_case_identifiers(self):
        """CamelCase and other mixed case identifiers."""
        assert not is_keyword('MyClass')
        assert not is_keyword('getUserName')
        assert not is_keyword('HTTPServer')

        assert get_keyword_type('MyClass') == TokenType.IDENTIFIER
        assert get_keyword_type('getUserName') == TokenType.IDENTIFIER
        assert get_keyword_type('HTTPServer') == TokenType.IDENTIFIER


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Empty string is not a keyword."""
        assert not is_keyword('')
        assert get_keyword_type('') == TokenType.IDENTIFIER

    def test_single_character(self):
        """Single characters are not keywords (except potential future additions)."""
        assert not is_keyword('a')
        assert not is_keyword('x')
        assert not is_keyword('i')

        assert get_keyword_type('a') == TokenType.IDENTIFIER
        assert get_keyword_type('x') == TokenType.IDENTIFIER
        assert get_keyword_type('i') == TokenType.IDENTIFIER

    def test_numbers_in_identifiers(self):
        """Identifiers with numbers (note: lexer will handle leading digits separately)."""
        assert not is_keyword('var1')
        assert not is_keyword('user123')

        assert get_keyword_type('var1') == TokenType.IDENTIFIER
        assert get_keyword_type('user123') == TokenType.IDENTIFIER

    def test_special_case_enum(self):
        """Both 'Enum' and 'enum' should map to same TokenType."""
        assert get_keyword_type('Enum') == TokenType.ENUM
        assert get_keyword_type('enum') == TokenType.ENUM
        assert get_keyword_type('Enum') == get_keyword_type('enum')


class TestComprehensiveCoverage:
    """Verify all keywords are tested."""

    def test_all_keywords_tested(self):
        """Ensure every keyword in KEYWORDS table is valid."""
        for keyword in KEYWORDS.keys():
            # Should be recognized as keyword
            assert is_keyword(keyword), f"Keyword '{keyword}' not recognized"

            # Should map to a TokenType
            token_type = get_keyword_type(keyword)
            assert token_type != TokenType.IDENTIFIER, \
                f"Keyword '{keyword}' incorrectly mapped to IDENTIFIER"
            assert isinstance(token_type, TokenType), \
                f"Keyword '{keyword}' did not map to TokenType"
