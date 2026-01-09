"""Tests for expression code generation in Fusion compiler.

Tests all expression visitor methods in CCodeGenerator:
- Literal expressions (int, float, double, bool, char, string, null)
- Identifier expressions
- Binary operations (arithmetic, comparison, logical)
- Unary operations (-, not, !)
- Function calls
- String interpolation
"""

import pytest
from src.codegen.c_generator import CCodeGenerator
from src.parser.ast_nodes import (
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr,
    CallExpr, InterpolatedStringExpr
)
from src.lexer.token import SourceLocation


# Helper to create a dummy location
def loc():
    """Create dummy source location for tests."""
    return SourceLocation("test.fusion", 1, 1)


class TestLiteralExpressions:
    """Test literal expression code generation."""

    def test_integer_literal(self):
        """Test integer literal: 42 → 42"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value=42, type_hint='int')
        result = gen.visit_LiteralExpr(node)
        assert result == '42'

    def test_float_literal(self):
        """Test float literal: 3.14 → 3.14f"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value=3.14, type_hint='float')
        result = gen.visit_LiteralExpr(node)
        assert result == '3.14f'

    def test_double_literal(self):
        """Test double literal: 3.14159 → 3.14159"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value=3.14159, type_hint='double')
        result = gen.visit_LiteralExpr(node)
        assert result == '3.14159'

    def test_boolean_true(self):
        """Test boolean true: true → true"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value=True, type_hint='bool')
        result = gen.visit_LiteralExpr(node)
        assert result == 'true'

    def test_boolean_false(self):
        """Test boolean false: false → false"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value=False, type_hint='bool')
        result = gen.visit_LiteralExpr(node)
        assert result == 'false'

    def test_character_literal(self):
        """Test character: 'a' → 'a'"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value='a', type_hint='char')
        result = gen.visit_LiteralExpr(node)
        assert result == "'a'"

    def test_string_literal(self):
        """Test string: "hello" → "hello" """
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value='hello', type_hint='string')
        result = gen.visit_LiteralExpr(node)
        assert result == '"hello"'

    def test_string_with_escape(self):
        """Test string with newline escape"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value='hello\n', type_hint='string')
        result = gen.visit_LiteralExpr(node)
        assert result == '"hello\\n"'

    def test_null_literal(self):
        """Test null: null → NULL"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value=None, type_hint='null')
        result = gen.visit_LiteralExpr(node)
        assert result == 'NULL'

    def test_char_with_escape(self):
        """Test character with newline escape"""
        gen = CCodeGenerator()
        node = LiteralExpr(location=loc(), value='\n', type_hint='char')
        result = gen.visit_LiteralExpr(node)
        assert result == "'\\n'"


class TestIdentifierExpressions:
    """Test identifier expression code generation."""

    def test_simple_variable(self):
        """Test simple variable: x → x"""
        gen = CCodeGenerator()
        node = IdentifierExpr(location=loc(), name='x')
        result = gen.visit_IdentifierExpr(node)
        assert result == 'x'

    def test_parameter(self):
        """Test parameter: param → param"""
        gen = CCodeGenerator()
        node = IdentifierExpr(location=loc(), name='param')
        result = gen.visit_IdentifierExpr(node)
        assert result == 'param'

    def test_function_name(self):
        """Test function name: add → add"""
        gen = CCodeGenerator()
        node = IdentifierExpr(location=loc(), name='add')
        result = gen.visit_IdentifierExpr(node)
        assert result == 'add'


class TestBinaryOperations:
    """Test binary operation code generation."""

    def test_addition(self):
        """Test addition: a + b → (a + b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='+', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a + b)'

    def test_subtraction(self):
        """Test subtraction: a - b → (a - b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='-', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a - b)'

    def test_multiplication(self):
        """Test multiplication: a * b → (a * b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='*', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a * b)'

    def test_division(self):
        """Test division: a / b → (a / b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='/', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a / b)'

    def test_modulo(self):
        """Test modulo: a % b → (a % b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='%', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a % b)'

    def test_less_than(self):
        """Test less than: a < b → (a < b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='<', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a < b)'

    def test_greater_than(self):
        """Test greater than: a > b → (a > b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='>', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a > b)'

    def test_equals(self):
        """Test equals: a == b → (a == b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='==', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a == b)'

    def test_not_equals(self):
        """Test not equals: a != b → (a != b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='!=', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a != b)'

    def test_logical_and(self):
        """Test logical and: a and b → (a && b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='and', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a && b)'

    def test_logical_or(self):
        """Test logical or: a or b → (a || b)"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='or', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == '(a || b)'

    def test_power(self):
        """Test power: a ** b → pow(a, b) and adds math.h"""
        gen = CCodeGenerator()
        left = IdentifierExpr(location=loc(), name='a')
        right = IdentifierExpr(location=loc(), name='b')
        node = BinaryExpr(location=loc(), left=left, operator='**', right=right)
        result = gen.visit_BinaryExpr(node)
        assert result == 'pow(a, b)'
        assert '<math.h>' in gen.includes


class TestUnaryOperations:
    """Test unary operation code generation."""

    def test_negation(self):
        """Test negation: -x → (-x)"""
        gen = CCodeGenerator()
        operand = IdentifierExpr(location=loc(), name='x')
        node = UnaryExpr(location=loc(), operator='-', operand=operand)
        result = gen.visit_UnaryExpr(node)
        assert result == '(-x)'

    def test_logical_not_word(self):
        """Test logical not (word): not x → (!x)"""
        gen = CCodeGenerator()
        operand = IdentifierExpr(location=loc(), name='x')
        node = UnaryExpr(location=loc(), operator='not', operand=operand)
        result = gen.visit_UnaryExpr(node)
        assert result == '(!x)'

    def test_logical_not_symbol(self):
        """Test logical not (symbol): !x → (!x)"""
        gen = CCodeGenerator()
        operand = IdentifierExpr(location=loc(), name='x')
        node = UnaryExpr(location=loc(), operator='!', operand=operand)
        result = gen.visit_UnaryExpr(node)
        assert result == '(!x)'


class TestFunctionCalls:
    """Test function call code generation."""

    def test_simple_call(self):
        """Test simple call: add(1, 2) → add(1, 2)"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='add')
        arg1 = LiteralExpr(location=loc(), value=1, type_hint='int')
        arg2 = LiteralExpr(location=loc(), value=2, type_hint='int')
        node = CallExpr(location=loc(), callee=callee, arguments=[arg1, arg2])
        result = gen.visit_CallExpr(node)
        assert result == 'add(1, 2)'

    def test_no_args(self):
        """Test no args: foo() → foo()"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='foo')
        node = CallExpr(location=loc(), callee=callee, arguments=[])
        result = gen.visit_CallExpr(node)
        assert result == 'foo()'

    def test_nested_call(self):
        """Test nested call: add(mul(2, 3), 4) → add(mul(2, 3), 4)"""
        gen = CCodeGenerator()

        # Inner call: mul(2, 3)
        mul_callee = IdentifierExpr(location=loc(), name='mul')
        mul_arg1 = LiteralExpr(location=loc(), value=2, type_hint='int')
        mul_arg2 = LiteralExpr(location=loc(), value=3, type_hint='int')
        mul_call = CallExpr(location=loc(), callee=mul_callee, arguments=[mul_arg1, mul_arg2])

        # Outer call: add(..., 4)
        add_callee = IdentifierExpr(location=loc(), name='add')
        add_arg2 = LiteralExpr(location=loc(), value=4, type_hint='int')
        node = CallExpr(location=loc(), callee=add_callee, arguments=[mul_call, add_arg2])

        result = gen.visit_CallExpr(node)
        assert result == 'add(mul(2, 3), 4)'

    def test_print_string(self):
        """Test print string: print("hello") → printf("hello\\n")"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='print')
        arg = LiteralExpr(location=loc(), value='hello', type_hint='string')
        node = CallExpr(location=loc(), callee=callee, arguments=[arg])
        result = gen.visit_CallExpr(node)
        assert result == 'printf("hello\\n")'

    def test_print_empty(self):
        """Test print empty: print() → printf("\\n")"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='print')
        node = CallExpr(location=loc(), callee=callee, arguments=[])
        result = gen.visit_CallExpr(node)
        assert result == 'printf("\\n")'

    def test_print_with_variable(self):
        """Test print with interpolation: print("{x}") → printf("%d\\n", x)"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='print')

        # Create interpolated string: "{x}"
        x_ident = IdentifierExpr(location=loc(), name='x')
        interp_string = InterpolatedStringExpr(
            location=loc(),
            parts=['', ''],  # Empty string before and after {x}
            expressions=[x_ident]
        )

        node = CallExpr(location=loc(), callee=callee, arguments=[interp_string])
        result = gen.visit_CallExpr(node)
        assert result == 'printf("%d\\n", x)'

    def test_print_with_multiple_vars(self):
        """Test print with multiple vars: print("{x} and {y}") → printf("%d and %d\\n", x, y)"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='print')

        # Create interpolated string: "{x} and {y}"
        x_ident = IdentifierExpr(location=loc(), name='x')
        y_ident = IdentifierExpr(location=loc(), name='y')
        interp_string = InterpolatedStringExpr(
            location=loc(),
            parts=['', ' and ', ''],  # Parts: "", " and ", ""
            expressions=[x_ident, y_ident]
        )

        node = CallExpr(location=loc(), callee=callee, arguments=[interp_string])
        result = gen.visit_CallExpr(node)
        assert result == 'printf("%d and %d\\n", x, y)'


class TestStringInterpolation:
    """Test string interpolation code generation."""

    def test_simple_interpolation(self):
        """Test simple interpolation: "Value: {x}" """
        gen = CCodeGenerator()
        x_ident = IdentifierExpr(location=loc(), name='x')
        node = InterpolatedStringExpr(
            location=loc(),
            parts=['Value: ', ''],
            expressions=[x_ident]
        )
        result = gen.visit_InterpolatedStringExpr(node)
        assert result == '"Value: %d", x'

    def test_multiple_interpolations(self):
        """Test multiple interpolations: "{a} + {b} = {c}" """
        gen = CCodeGenerator()
        a_ident = IdentifierExpr(location=loc(), name='a')
        b_ident = IdentifierExpr(location=loc(), name='b')
        c_ident = IdentifierExpr(location=loc(), name='c')
        node = InterpolatedStringExpr(
            location=loc(),
            parts=['', ' + ', ' = ', ''],
            expressions=[a_ident, b_ident, c_ident]
        )
        result = gen.visit_InterpolatedStringExpr(node)
        assert result == '"%d + %d = %d", a, b, c'

    def test_interpolated_print(self):
        """Test _generate_interpolated_print directly"""
        gen = CCodeGenerator()
        x_ident = IdentifierExpr(location=loc(), name='x')
        node = InterpolatedStringExpr(
            location=loc(),
            parts=['Result: ', ''],
            expressions=[x_ident]
        )
        result = gen._generate_interpolated_print(node)
        assert result == 'printf("Result: %d\\n", x)'


class TestComplexExpressions:
    """Test complex nested expressions."""

    def test_nested_binary_operations(self):
        """Test nested binary: (a + b) * c → ((a + b) * c)"""
        gen = CCodeGenerator()
        a = IdentifierExpr(location=loc(), name='a')
        b = IdentifierExpr(location=loc(), name='b')
        c = IdentifierExpr(location=loc(), name='c')

        add = BinaryExpr(location=loc(), left=a, operator='+', right=b)
        mul = BinaryExpr(location=loc(), left=add, operator='*', right=c)

        result = gen.visit_BinaryExpr(mul)
        assert result == '((a + b) * c)'

    def test_unary_in_binary(self):
        """Test unary in binary: -a + b → ((-a) + b)"""
        gen = CCodeGenerator()
        a = IdentifierExpr(location=loc(), name='a')
        b = IdentifierExpr(location=loc(), name='b')

        neg_a = UnaryExpr(location=loc(), operator='-', operand=a)
        add = BinaryExpr(location=loc(), left=neg_a, operator='+', right=b)

        result = gen.visit_BinaryExpr(add)
        assert result == '((-a) + b)'

    def test_function_call_in_binary(self):
        """Test function call in binary: add(1, 2) + 3 → (add(1, 2) + 3)"""
        gen = CCodeGenerator()

        # add(1, 2)
        callee = IdentifierExpr(location=loc(), name='add')
        arg1 = LiteralExpr(location=loc(), value=1, type_hint='int')
        arg2 = LiteralExpr(location=loc(), value=2, type_hint='int')
        call = CallExpr(location=loc(), callee=callee, arguments=[arg1, arg2])

        # ... + 3
        three = LiteralExpr(location=loc(), value=3, type_hint='int')
        binary = BinaryExpr(location=loc(), left=call, operator='+', right=three)

        result = gen.visit_BinaryExpr(binary)
        assert result == '(add(1, 2) + 3)'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
