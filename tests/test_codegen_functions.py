"""Tests for function and declaration code generation in Fusion compiler.

Tests all function/declaration visitor methods in CCodeGenerator:
- Function declarations
- Lambda functions
- Parameters
- Program structure
- Complete programs
"""

import pytest
from src.codegen.c_generator import CCodeGenerator
from src.parser.ast_nodes import (
    LiteralExpr, IdentifierExpr, BinaryExpr,
    VarDeclStmt, AssignmentStmt, ReturnStmt, ExpressionStmt,
    IfStmt, WhileStmt, BlockStmt,
    FunctionDecl, ParameterDecl, ProgramNode,
    PrimitiveType, CallExpr
)
from src.lexer.token import SourceLocation


# Helper to create a dummy location
def loc():
    """Create dummy source location for tests."""
    return SourceLocation("test.fusion", 1, 1)


class TestFunctionDeclarations:
    """Test function declaration code generation."""

    def test_simple_void_function_no_params(self):
        """Test simple void function with no params"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='void')
        body = BlockStmt(location=loc(), statements=[])
        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='foo',
            parameters=[],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'void foo(void) {' in output
        assert '}' in output

    def test_function_with_return_type(self):
        """Test function with return type"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')
        ret_stmt = ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=42, type_hint='int'))
        body = BlockStmt(location=loc(), statements=[ret_stmt])
        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='getNumber',
            parameters=[],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int getNumber(void) {' in output
        assert 'return 42;' in output

    def test_function_with_single_parameter(self):
        """Test function with single parameter"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')
        param_type = PrimitiveType(location=loc(), name='int')
        param = ParameterDecl(location=loc(), param_type=param_type, name='x', default_value=None)

        ret_stmt = ReturnStmt(location=loc(), value=IdentifierExpr(location=loc(), name='x'))
        body = BlockStmt(location=loc(), statements=[ret_stmt])

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='identity',
            parameters=[param],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int identity(int x) {' in output
        assert 'return x;' in output

    def test_function_with_multiple_parameters(self):
        """Test function with multiple parameters"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')

        param1 = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='a',
            default_value=None
        )
        param2 = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='b',
            default_value=None
        )

        # return a + b
        a_id = IdentifierExpr(location=loc(), name='a')
        b_id = IdentifierExpr(location=loc(), name='b')
        add_expr = BinaryExpr(location=loc(), left=a_id, operator='+', right=b_id)
        ret_stmt = ReturnStmt(location=loc(), value=add_expr)
        body = BlockStmt(location=loc(), statements=[ret_stmt])

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='add',
            parameters=[param1, param2],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int add(int a, int b) {' in output
        assert 'return (a + b);' in output

    def test_function_with_local_variables(self):
        """Test function with local variables"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')

        # int x = 5;
        var_decl = VarDeclStmt(
            location=loc(),
            var_type=PrimitiveType(location=loc(), name='int'),
            name='x',
            initializer=LiteralExpr(location=loc(), value=5, type_hint='int')
        )

        # return x;
        ret_stmt = ReturnStmt(location=loc(), value=IdentifierExpr(location=loc(), name='x'))

        body = BlockStmt(location=loc(), statements=[var_decl, ret_stmt])

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='test',
            parameters=[],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int test(void) {' in output
        assert 'int x = 5;' in output
        assert 'return x;' in output

    def test_function_with_if_statement(self):
        """Test function with if statement"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')

        param = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='x',
            default_value=None
        )

        # if x > 0 { return 1; }
        x_id = IdentifierExpr(location=loc(), name='x')
        zero = LiteralExpr(location=loc(), value=0, type_hint='int')
        cond = BinaryExpr(location=loc(), left=x_id, operator='>', right=zero)

        then_body = BlockStmt(location=loc(), statements=[
            ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=1, type_hint='int'))
        ])

        if_stmt = IfStmt(location=loc(), condition=cond, then_branch=then_body, else_branch=None)

        body = BlockStmt(location=loc(), statements=[if_stmt])

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='test',
            parameters=[param],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int test(int x) {' in output
        assert 'if ((x > 0)) {' in output
        assert 'return 1;' in output

    def test_recursive_function(self):
        """Test recursive function (factorial)"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')

        param = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='n',
            default_value=None
        )

        # if n <= 1 { return 1; }
        n_id = IdentifierExpr(location=loc(), name='n')
        one = LiteralExpr(location=loc(), value=1, type_hint='int')
        cond = BinaryExpr(location=loc(), left=n_id, operator='<=', right=one)

        then_body = BlockStmt(location=loc(), statements=[
            ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=1, type_hint='int'))
        ])

        if_stmt = IfStmt(location=loc(), condition=cond, then_branch=then_body, else_branch=None)

        # return n * factorial(n - 1);
        factorial_call = CallExpr(
            location=loc(),
            callee=IdentifierExpr(location=loc(), name='factorial'),
            arguments=[BinaryExpr(
                location=loc(),
                left=IdentifierExpr(location=loc(), name='n'),
                operator='-',
                right=LiteralExpr(location=loc(), value=1, type_hint='int')
            )]
        )

        mult = BinaryExpr(
            location=loc(),
            left=IdentifierExpr(location=loc(), name='n'),
            operator='*',
            right=factorial_call
        )

        ret_stmt = ReturnStmt(location=loc(), value=mult)

        body = BlockStmt(location=loc(), statements=[if_stmt, ret_stmt])

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='factorial',
            parameters=[param],
            body=body,
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int factorial(int n) {' in output
        assert 'if ((n <= 1)) {' in output
        assert 'return (n * factorial((n - 1)));' in output


class TestLambdaFunctions:
    """Test lambda function code generation."""

    def test_inline_lambda(self):
        """Test inline lambda: int add(int a, int b) : a + b"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')

        param1 = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='a',
            default_value=None
        )
        param2 = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='b',
            default_value=None
        )

        # Body: a + b (expression)
        a_id = IdentifierExpr(location=loc(), name='a')
        b_id = IdentifierExpr(location=loc(), name='b')
        add_expr = BinaryExpr(location=loc(), left=a_id, operator='+', right=b_id)

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='add',
            parameters=[param1, param2],
            body=add_expr,  # Direct expression
            is_lambda=True
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int add(int a, int b) {' in output
        assert 'return (a + b);' in output

    def test_lambda_with_single_return(self):
        """Test lambda with explicit return statement"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='int')

        # Body: return 42;
        ret_stmt = ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=42, type_hint='int'))
        body = BlockStmt(location=loc(), statements=[ret_stmt])

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='getNumber',
            parameters=[],
            body=body,
            is_lambda=True
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'int getNumber(void) {' in output
        assert 'return 42;' in output

    def test_lambda_void_with_expression(self):
        """Test void lambda with expression (print call)"""
        gen = CCodeGenerator()
        return_type = PrimitiveType(location=loc(), name='void')

        # Body: print("hello")
        print_call = CallExpr(
            location=loc(),
            callee=IdentifierExpr(location=loc(), name='print'),
            arguments=[LiteralExpr(location=loc(), value='hello', type_hint='string')]
        )

        func = FunctionDecl(
            location=loc(),
            return_type=return_type,
            name='greet',
            parameters=[],
            body=print_call,
            is_lambda=True
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'void greet(void) {' in output
        assert 'printf("hello\\n");' in output


class TestProgramStructure:
    """Test complete program structure generation."""

    def test_single_function_program(self):
        """Test single function program"""
        gen = CCodeGenerator()

        # void main() { }
        main_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='main',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[]),
            is_lambda=False
        )

        program = ProgramNode(location=loc(), declarations=[main_func])
        result = gen.generate(program)

        assert '#include <stdio.h>' in result
        assert '#include <stdbool.h>' in result
        assert '// Forward declarations' in result
        assert 'int main(void);' in result
        assert 'int main(void) {' in result
        assert 'return 0;' in result  # Auto-added for void main

    def test_two_function_program(self):
        """Test two function program"""
        gen = CCodeGenerator()

        # int add(int a, int b) : a + b
        add_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='int'),
            name='add',
            parameters=[
                ParameterDecl(
                    location=loc(),
                    param_type=PrimitiveType(location=loc(), name='int'),
                    name='a',
                    default_value=None
                ),
                ParameterDecl(
                    location=loc(),
                    param_type=PrimitiveType(location=loc(), name='int'),
                    name='b',
                    default_value=None
                )
            ],
            body=BinaryExpr(
                location=loc(),
                left=IdentifierExpr(location=loc(), name='a'),
                operator='+',
                right=IdentifierExpr(location=loc(), name='b')
            ),
            is_lambda=True
        )

        # void main() { }
        main_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='main',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[]),
            is_lambda=False
        )

        program = ProgramNode(location=loc(), declarations=[add_func, main_func])
        result = gen.generate(program)

        # Check forward declarations
        assert 'int add(int a, int b);' in result
        assert 'int main(void);' in result

        # Check add function comes before main
        add_pos = result.index('int add(int a, int b) {')
        main_pos = result.index('int main(void) {')
        assert add_pos < main_pos

    def test_main_function_last(self):
        """Test that main function is generated last"""
        gen = CCodeGenerator()

        # Create main first, then helper functions
        main_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='main',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[]),
            is_lambda=False
        )

        helper_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='int'),
            name='helper',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[
                ReturnStmt(location=loc(), value=LiteralExpr(location=loc(), value=0, type_hint='int'))
            ]),
            is_lambda=False
        )

        # Add main first in declaration list
        program = ProgramNode(location=loc(), declarations=[main_func, helper_func])
        result = gen.generate(program)

        # Main should come after helper in generated code
        helper_pos = result.index('int helper(void) {')
        main_pos = result.index('int main(void) {')
        assert helper_pos < main_pos

    def test_complete_hello_world(self):
        """Test complete Hello World program"""
        gen = CCodeGenerator()

        # void main() { print("Hello, World!"); }
        print_call = CallExpr(
            location=loc(),
            callee=IdentifierExpr(location=loc(), name='print'),
            arguments=[LiteralExpr(location=loc(), value='Hello, World!', type_hint='string')]
        )

        print_stmt = ExpressionStmt(location=loc(), expression=print_call)

        main_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='main',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[print_stmt]),
            is_lambda=False
        )

        program = ProgramNode(location=loc(), declarations=[main_func])
        result = gen.generate(program)

        assert '#include <stdio.h>' in result
        assert 'int main(void) {' in result
        assert 'printf("Hello, World!\\n");' in result
        assert 'return 0;' in result  # Auto-added for void main

    def test_complete_program_with_helpers(self):
        """Test complete program with helper functions"""
        gen = CCodeGenerator()

        # int add(int a, int b) { return a + b; }
        add_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='int'),
            name='add',
            parameters=[
                ParameterDecl(
                    location=loc(),
                    param_type=PrimitiveType(location=loc(), name='int'),
                    name='a',
                    default_value=None
                ),
                ParameterDecl(
                    location=loc(),
                    param_type=PrimitiveType(location=loc(), name='int'),
                    name='b',
                    default_value=None
                )
            ],
            body=BinaryExpr(
                location=loc(),
                left=IdentifierExpr(location=loc(), name='a'),
                operator='+',
                right=IdentifierExpr(location=loc(), name='b')
            ),
            is_lambda=True
        )

        # void main() { int result = add(5, 3); }
        add_call = CallExpr(
            location=loc(),
            callee=IdentifierExpr(location=loc(), name='add'),
            arguments=[
                LiteralExpr(location=loc(), value=5, type_hint='int'),
                LiteralExpr(location=loc(), value=3, type_hint='int')
            ]
        )

        var_decl = VarDeclStmt(
            location=loc(),
            var_type=PrimitiveType(location=loc(), name='int'),
            name='result',
            initializer=add_call
        )

        main_func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='main',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[var_decl]),
            is_lambda=False
        )

        program = ProgramNode(location=loc(), declarations=[add_func, main_func])
        result = gen.generate(program)

        # Check structure
        assert '#include <stdio.h>' in result
        assert 'int add(int a, int b);' in result
        assert 'int main(void);' in result
        assert 'int add(int a, int b) {' in result
        assert 'return (a + b);' in result
        assert 'int main(void) {' in result
        assert 'int result = add(5, 3);' in result


class TestParameters:
    """Test parameter handling."""

    def test_no_parameters_void(self):
        """Test function with no parameters generates (void)"""
        gen = CCodeGenerator()

        func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='test',
            parameters=[],
            body=BlockStmt(location=loc(), statements=[]),
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'void test(void) {' in output

    def test_multiple_parameter_types(self):
        """Test different parameter types"""
        gen = CCodeGenerator()

        params = [
            ParameterDecl(
                location=loc(),
                param_type=PrimitiveType(location=loc(), name='int'),
                name='x',
                default_value=None
            ),
            ParameterDecl(
                location=loc(),
                param_type=PrimitiveType(location=loc(), name='float'),
                name='y',
                default_value=None
            ),
            ParameterDecl(
                location=loc(),
                param_type=PrimitiveType(location=loc(), name='string'),
                name='s',
                default_value=None
            ),
            ParameterDecl(
                location=loc(),
                param_type=PrimitiveType(location=loc(), name='bool'),
                name='flag',
                default_value=None
            )
        ]

        func = FunctionDecl(
            location=loc(),
            return_type=PrimitiveType(location=loc(), name='void'),
            name='test',
            parameters=params,
            body=BlockStmt(location=loc(), statements=[]),
            is_lambda=False
        )

        gen.visit_FunctionDecl(func)
        output = '\n'.join(gen.output)
        assert 'void test(int x, float y, char* s, bool flag) {' in output

    def test_visit_parameter_decl_directly(self):
        """Test visiting ParameterDecl directly"""
        gen = CCodeGenerator()

        param = ParameterDecl(
            location=loc(),
            param_type=PrimitiveType(location=loc(), name='int'),
            name='x',
            default_value=None
        )

        result = gen.visit_ParameterDecl(param)
        assert result == 'int x'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
