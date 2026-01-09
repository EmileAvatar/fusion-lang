"""Tests for statement code generation in Fusion compiler.

Tests all statement visitor methods in CCodeGenerator:
- Variable declarations
- Assignments
- Return statements
- If/else statements
- While loops
- For loops
- Break/continue statements
- Expression statements
- Block statements
"""

import pytest
from src.codegen.c_generator import CCodeGenerator
from src.parser.ast_nodes import (
    LiteralExpr, IdentifierExpr, BinaryExpr, CallExpr,
    ExpressionStmt, VarDeclStmt, AssignmentStmt, ReturnStmt,
    IfStmt, WhileStmt, ForStmt, BreakStmt, ContinueStmt, BlockStmt,
    PrimitiveType
)
from src.lexer.token import SourceLocation


# Helper to create a dummy location
def loc():
    """Create dummy source location for tests."""
    return SourceLocation("test.fusion", 1, 1)


class TestVariableDeclarations:
    """Test variable declaration code generation."""

    def test_simple_int_declaration(self):
        """Test simple int: int x → int x;"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='int')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='x', initializer=None)
        gen.visit_VarDeclStmt(node)
        assert 'int x;' in '\n'.join(gen.output)

    def test_declaration_with_initializer(self):
        """Test with initializer: int x = 5 → int x = 5;"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='int')
        init = LiteralExpr(location=loc(), value=5, type_hint='int')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='x', initializer=init)
        gen.visit_VarDeclStmt(node)
        assert 'int x = 5;' in '\n'.join(gen.output)

    def test_float_declaration(self):
        """Test float: float y = 3.14 → float y = 3.14f;"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='float')
        init = LiteralExpr(location=loc(), value=3.14, type_hint='float')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='y', initializer=init)
        gen.visit_VarDeclStmt(node)
        assert 'float y = 3.14f;' in '\n'.join(gen.output)

    def test_bool_declaration(self):
        """Test bool: bool flag = true → bool flag = true;"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='bool')
        init = LiteralExpr(location=loc(), value=True, type_hint='bool')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='flag', initializer=init)
        gen.visit_VarDeclStmt(node)
        assert 'bool flag = true;' in '\n'.join(gen.output)

    def test_string_declaration(self):
        """Test string: string s = "hello" → char* s = "hello";"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='string')
        init = LiteralExpr(location=loc(), value='hello', type_hint='string')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='s', initializer=init)
        gen.visit_VarDeclStmt(node)
        assert 'char* s = "hello";' in '\n'.join(gen.output)

    def test_declaration_with_expression(self):
        """Test declaration with expression: int x = a + b"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='int')
        a = IdentifierExpr(location=loc(), name='a')
        b = IdentifierExpr(location=loc(), name='b')
        expr = BinaryExpr(location=loc(), left=a, operator='+', right=b)
        node = VarDeclStmt(location=loc(), var_type=var_type, name='x', initializer=expr)
        gen.visit_VarDeclStmt(node)
        assert 'int x = (a + b);' in '\n'.join(gen.output)

    def test_double_declaration(self):
        """Test double: double pi = 3.14159 → double pi = 3.14159;"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='double')
        init = LiteralExpr(location=loc(), value=3.14159, type_hint='double')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='pi', initializer=init)
        gen.visit_VarDeclStmt(node)
        assert 'double pi = 3.14159;' in '\n'.join(gen.output)

    def test_char_declaration(self):
        """Test char: char c = 'a' → char c = 'a';"""
        gen = CCodeGenerator()
        var_type = PrimitiveType(location=loc(), name='char')
        init = LiteralExpr(location=loc(), value='a', type_hint='char')
        node = VarDeclStmt(location=loc(), var_type=var_type, name='c', initializer=init)
        gen.visit_VarDeclStmt(node)
        assert "char c = 'a';" in '\n'.join(gen.output)


class TestAssignments:
    """Test assignment statement code generation."""

    def test_simple_assignment(self):
        """Test simple assignment: x = 5 → x = 5;"""
        gen = CCodeGenerator()
        target = IdentifierExpr(location=loc(), name='x')
        value = LiteralExpr(location=loc(), value=5, type_hint='int')
        node = AssignmentStmt(location=loc(), target=target, value=value)
        gen.visit_AssignmentStmt(node)
        assert 'x = 5;' in '\n'.join(gen.output)

    def test_expression_assignment(self):
        """Test expression assignment: x = a + b → x = (a + b);"""
        gen = CCodeGenerator()
        target = IdentifierExpr(location=loc(), name='x')
        a = IdentifierExpr(location=loc(), name='a')
        b = IdentifierExpr(location=loc(), name='b')
        value = BinaryExpr(location=loc(), left=a, operator='+', right=b)
        node = AssignmentStmt(location=loc(), target=target, value=value)
        gen.visit_AssignmentStmt(node)
        assert 'x = (a + b);' in '\n'.join(gen.output)

    def test_string_assignment(self):
        """Test string assignment: s = "hello" → s = "hello";"""
        gen = CCodeGenerator()
        target = IdentifierExpr(location=loc(), name='s')
        value = LiteralExpr(location=loc(), value='hello', type_hint='string')
        node = AssignmentStmt(location=loc(), target=target, value=value)
        gen.visit_AssignmentStmt(node)
        assert 's = "hello";' in '\n'.join(gen.output)

    def test_boolean_assignment(self):
        """Test boolean assignment: flag = false → flag = false;"""
        gen = CCodeGenerator()
        target = IdentifierExpr(location=loc(), name='flag')
        value = LiteralExpr(location=loc(), value=False, type_hint='bool')
        node = AssignmentStmt(location=loc(), target=target, value=value)
        gen.visit_AssignmentStmt(node)
        assert 'flag = false;' in '\n'.join(gen.output)


class TestReturnStatements:
    """Test return statement code generation."""

    def test_return_value(self):
        """Test return value: return 42 → return 42;"""
        gen = CCodeGenerator()
        value = LiteralExpr(location=loc(), value=42, type_hint='int')
        node = ReturnStmt(location=loc(), value=value)
        gen.visit_ReturnStmt(node)
        assert 'return 42;' in '\n'.join(gen.output)

    def test_return_expression(self):
        """Test return expression: return a + b → return (a + b);"""
        gen = CCodeGenerator()
        a = IdentifierExpr(location=loc(), name='a')
        b = IdentifierExpr(location=loc(), name='b')
        value = BinaryExpr(location=loc(), left=a, operator='+', right=b)
        node = ReturnStmt(location=loc(), value=value)
        gen.visit_ReturnStmt(node)
        assert 'return (a + b);' in '\n'.join(gen.output)

    def test_return_void(self):
        """Test return void: return → return;"""
        gen = CCodeGenerator()
        node = ReturnStmt(location=loc(), value=None)
        gen.visit_ReturnStmt(node)
        assert 'return;' in '\n'.join(gen.output)

    def test_return_variable(self):
        """Test return variable: return x → return x;"""
        gen = CCodeGenerator()
        value = IdentifierExpr(location=loc(), name='x')
        node = ReturnStmt(location=loc(), value=value)
        gen.visit_ReturnStmt(node)
        assert 'return x;' in '\n'.join(gen.output)

    def test_return_function_call(self):
        """Test return function call: return foo() → return foo();"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='foo')
        call = CallExpr(location=loc(), callee=callee, arguments=[])
        node = ReturnStmt(location=loc(), value=call)
        gen.visit_ReturnStmt(node)
        assert 'return foo();' in '\n'.join(gen.output)


class TestIfStatements:
    """Test if statement code generation."""

    def test_simple_if(self):
        """Test simple if: if x > 0 { ... }"""
        gen = CCodeGenerator()
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        condition = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Body: return x;
        ret_val = IdentifierExpr(location=loc(), name='x')
        ret_stmt = ReturnStmt(location=loc(), value=ret_val)
        body = BlockStmt(location=loc(), statements=[ret_stmt])

        node = IfStmt(location=loc(), condition=condition, then_branch=body, else_branch=None)
        gen.visit_IfStmt(node)

        output = '\n'.join(gen.output)
        assert 'if ((x > 0)) {' in output
        assert 'return x;' in output
        assert '}' in output

    def test_if_with_else(self):
        """Test if with else: if x > 0 { ... } else { ... }"""
        gen = CCodeGenerator()
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        condition = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Then body: return x;
        ret_x = ReturnStmt(location=loc(), value=IdentifierExpr(location=loc(), name='x'))
        then_body = BlockStmt(location=loc(), statements=[ret_x])

        # Else body: return 0;
        ret_zero = ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=0, type_hint='int'))
        else_body = BlockStmt(location=loc(), statements=[ret_zero])

        node = IfStmt(location=loc(), condition=condition, then_branch=then_body, else_branch=else_body)
        gen.visit_IfStmt(node)

        output = '\n'.join(gen.output)
        assert 'if ((x > 0)) {' in output
        assert '} else {' in output
        assert 'return x;' in output
        assert 'return 0;' in output

    def test_if_with_complex_condition(self):
        """Test if with complex condition: if a > 0 and b < 10"""
        gen = CCodeGenerator()
        a = IdentifierExpr(location=loc(), name='a')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        cond1 = BinaryExpr(location=loc(), left=a, operator='>', right=zero)

        b = IdentifierExpr(location=loc(), name='b')
        ten = LiteralExpr(location=loc(), value=10, type_hint='int')
        cond2 = BinaryExpr(location=loc(), left=b, operator='<', right=ten)

        condition = BinaryExpr(location=loc(), left=cond1, operator='and', right=cond2)

        # Empty body
        body = BlockStmt(location=loc(), statements=[])

        node = IfStmt(location=loc(), condition=condition, then_branch=body, else_branch=None)
        gen.visit_IfStmt(node)

        output = '\n'.join(gen.output)
        assert 'if (((a > 0) && (b < 10))) {' in output


class TestWhileLoops:
    """Test while loop code generation."""

    def test_simple_while(self):
        """Test simple while: while x > 0 { ... }"""
        gen = CCodeGenerator()
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        condition = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Body: x = x - 1;
        x_target = IdentifierExpr(location=loc(), name='x')
        x_val = IdentifierExpr(location=loc(), name='x')
        one = LiteralExpr(location=loc(), value=1, type_hint='int')
        expr = BinaryExpr(location=loc(), left=x_val, operator='-', right=one)
        assign = AssignmentStmt(location=loc(), target=x_target, value=expr)
        body = BlockStmt(location=loc(), statements=[assign])

        node = WhileStmt(location=loc(), condition=condition, body=body)
        gen.visit_WhileStmt(node)

        output = '\n'.join(gen.output)
        assert 'while ((x > 0)) {' in output
        assert 'x = (x - 1);' in output
        assert '}' in output

    def test_while_with_break(self):
        """Test while with break"""
        gen = CCodeGenerator()
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        condition = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Body: break;
        break_stmt = BreakStmt(location=loc())
        body = BlockStmt(location=loc(), statements=[break_stmt])

        node = WhileStmt(location=loc(), condition=condition, body=body)
        gen.visit_WhileStmt(node)

        output = '\n'.join(gen.output)
        assert 'while ((x > 0)) {' in output
        assert 'break;' in output

    def test_while_with_continue(self):
        """Test while with continue"""
        gen = CCodeGenerator()
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        condition = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Body: continue;
        continue_stmt = ContinueStmt(location=loc())
        body = BlockStmt(location=loc(), statements=[continue_stmt])

        node = WhileStmt(location=loc(), condition=condition, body=body)
        gen.visit_WhileStmt(node)

        output = '\n'.join(gen.output)
        assert 'while ((x > 0)) {' in output
        assert 'continue;' in output


class TestForLoops:
    """Test for loop code generation."""

    def test_simple_for(self):
        """Test simple for: for i in range(0, 10) → for (int i = 0; i < 10; i += 1)"""
        gen = CCodeGenerator()

        # Create range(0, 10) call
        range_func = IdentifierExpr(location=loc(), name='range')
        start = LiteralExpr(location=loc(), value=0, type_hint='int')
        end = LiteralExpr(location=loc(), value=10, type_hint='int')
        range_call = CallExpr(location=loc(), callee=range_func, arguments=[start, end])

        # Empty body
        body = BlockStmt(location=loc(), statements=[])

        node = ForStmt(location=loc(), variable='i', iterable=range_call, body=body)
        gen.visit_ForStmt(node)

        output = '\n'.join(gen.output)
        assert 'for (int i = 0; i < 10; i += 1) {' in output

    def test_for_with_step(self):
        """Test for with step: for i in range(0, 10, 2) → for (int i = 0; i < 10; i += 2)"""
        gen = CCodeGenerator()

        # Create range(0, 10, 2) call
        range_func = IdentifierExpr(location=loc(), name='range')
        start = LiteralExpr(location=loc(), value=0, type_hint='int')
        end = LiteralExpr(location=loc(), value=10, type_hint='int')
        step = LiteralExpr(location=loc(), value=2, type_hint='int')
        range_call = CallExpr(location=loc(), callee=range_func, arguments=[start, end, step])

        # Empty body
        body = BlockStmt(location=loc(), statements=[])

        node = ForStmt(location=loc(), variable='i', iterable=range_call, body=body)
        gen.visit_ForStmt(node)

        output = '\n'.join(gen.output)
        assert 'for (int i = 0; i < 10; i += 2) {' in output

    def test_for_with_expression(self):
        """Test for with expressions: for i in range(start, end)"""
        gen = CCodeGenerator()

        # Create range(start, end) call
        range_func = IdentifierExpr(location=loc(), name='range')
        start = IdentifierExpr(location=loc(), name='start')
        end = IdentifierExpr(location=loc(), name='end')
        range_call = CallExpr(location=loc(), callee=range_func, arguments=[start, end])

        # Empty body
        body = BlockStmt(location=loc(), statements=[])

        node = ForStmt(location=loc(), variable='i', iterable=range_call, body=body)
        gen.visit_ForStmt(node)

        output = '\n'.join(gen.output)
        assert 'for (int i = start; i < end; i += 1) {' in output

    def test_for_single_arg_range(self):
        """Test for with single arg range: for i in range(10) → for (int i = 0; i < 10; i += 1)"""
        gen = CCodeGenerator()

        # Create range(10) call
        range_func = IdentifierExpr(location=loc(), name='range')
        end = LiteralExpr(location=loc(), value=10, type_hint='int')
        range_call = CallExpr(location=loc(), callee=range_func, arguments=[end])

        # Empty body
        body = BlockStmt(location=loc(), statements=[])

        node = ForStmt(location=loc(), variable='i', iterable=range_call, body=body)
        gen.visit_ForStmt(node)

        output = '\n'.join(gen.output)
        assert 'for (int i = 0; i < 10; i += 1) {' in output


class TestBreakContinue:
    """Test break/continue statement code generation."""

    def test_break_statement(self):
        """Test break statement: break → break;"""
        gen = CCodeGenerator()
        node = BreakStmt(location=loc())
        gen.visit_BreakStmt(node)
        assert 'break;' in '\n'.join(gen.output)

    def test_continue_statement(self):
        """Test continue statement: continue → continue;"""
        gen = CCodeGenerator()
        node = ContinueStmt(location=loc())
        gen.visit_ContinueStmt(node)
        assert 'continue;' in '\n'.join(gen.output)


class TestExpressionStatements:
    """Test expression statement code generation."""

    def test_function_call_statement(self):
        """Test function call statement: print("hello")"""
        gen = CCodeGenerator()
        callee = IdentifierExpr(location=loc(), name='print')
        arg = LiteralExpr(location=loc(), value='hello', type_hint='string')
        call = CallExpr(location=loc(), callee=callee, arguments=[arg])
        node = ExpressionStmt(location=loc(), expression=call)
        gen.visit_ExpressionStmt(node)
        assert 'printf("hello\\n");' in '\n'.join(gen.output)

    def test_expression_statement(self):
        """Test simple expression statement: x + 1"""
        gen = CCodeGenerator()
        x = IdentifierExpr(location=loc(), name='x')
        one = LiteralExpr(location=loc(), value=1, type_hint='int')
        expr = BinaryExpr(location=loc(), left=x, operator='+', right=one)
        node = ExpressionStmt(location=loc(), expression=expr)
        gen.visit_ExpressionStmt(node)
        assert '(x + 1);' in '\n'.join(gen.output)


class TestBlockStatements:
    """Test block statement code generation."""

    def test_empty_block(self):
        """Test empty block"""
        gen = CCodeGenerator()
        node = BlockStmt(location=loc(), statements=[])
        gen.visit_BlockStmt(node)
        # Empty block should produce no output
        assert len(gen.output) == 0

    def test_block_with_single_statement(self):
        """Test block with single statement"""
        gen = CCodeGenerator()
        ret = ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=42, type_hint='int'))
        node = BlockStmt(location=loc(), statements=[ret])
        gen.visit_BlockStmt(node)
        assert 'return 42;' in '\n'.join(gen.output)

    def test_block_with_multiple_statements(self):
        """Test block with multiple statements"""
        gen = CCodeGenerator()

        # int x = 5;
        var_type = PrimitiveType(location=loc(), name='int')
        init = LiteralExpr(location=loc(), value=5, type_hint='int')
        var_decl = VarDeclStmt(location=loc(), var_type=var_type, name='x', initializer=init)

        # return x;
        ret = ReturnStmt(location=loc(), value=IdentifierExpr(location=loc(), name='x'))

        node = BlockStmt(location=loc(), statements=[var_decl, ret])
        gen.visit_BlockStmt(node)

        output = '\n'.join(gen.output)
        assert 'int x = 5;' in output
        assert 'return x;' in output


class TestComplexStatements:
    """Test complex nested statements."""

    def test_nested_if_statements(self):
        """Test nested if statements"""
        gen = CCodeGenerator()

        # Outer if: if x > 0
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        outer_cond = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Inner if: if x > 10
        ten = LiteralExpr(location=loc(), value=10, type_hint='int')
        inner_cond = BinaryExpr(location=loc(), left=x, operator='>', right=ten)

        # Inner body: return 10;
        inner_body = BlockStmt(location=loc(), statements=[
            ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=10, type_hint='int'))
        ])

        # Inner if statement
        inner_if = IfStmt(location=loc(), condition=inner_cond, then_branch=inner_body, else_branch=None)

        # Outer body: contains inner if
        outer_body = BlockStmt(location=loc(), statements=[inner_if])

        # Outer if statement
        outer_if = IfStmt(location=loc(), condition=outer_cond, then_branch=outer_body, else_branch=None)

        gen.visit_IfStmt(outer_if)

        output = '\n'.join(gen.output)
        assert 'if ((x > 0)) {' in output
        assert 'if ((x > 10)) {' in output
        assert 'return 10;' in output

    def test_if_with_multiple_statements_in_body(self):
        """Test if with multiple statements in body"""
        gen = CCodeGenerator()

        # Condition: x > 0
        x = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        condition = BinaryExpr(location=loc(), left=x, operator='>', right=zero)

        # Body: int y = x; return y;
        var_type = PrimitiveType(location=loc(), name='int')
        var_decl = VarDeclStmt(
            location=loc(),
            var_type=var_type,
            name='y',
            initializer=IdentifierExpr(location=loc(), name='x')
        )
        ret = ReturnStmt(location=loc(), value=IdentifierExpr(location=loc(), name='y'))
        body = BlockStmt(location=loc(), statements=[var_decl, ret])

        node = IfStmt(location=loc(), condition=condition, then_branch=body, else_branch=None)
        gen.visit_IfStmt(node)

        output = '\n'.join(gen.output)
        assert 'if ((x > 0)) {' in output
        assert 'int y = x;' in output
        assert 'return y;' in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
