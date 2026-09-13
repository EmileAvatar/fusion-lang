"""
Unit tests for AST node definitions.

Tests all AST node types for correct creation, field access, visitor pattern,
and string representation.
"""

import pytest
from src.parser.ast_nodes import *
from src.lexer.token import SourceLocation


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_location():
    """Fixture for test source location."""
    return SourceLocation("test.fusion", 1, 1)


# ============================================================================
# Base AST Node Tests
# ============================================================================

def test_ast_node_base(test_location):
    """Test base ASTNode class."""
    node = ASTNode(test_location)
    assert node.location == test_location
    assert node.location.filename == "test.fusion"
    assert node.location.line == 1
    assert node.location.column == 1


def test_visitor_pattern_implemented(test_location):
    """Test visitor pattern on LiteralExpr."""
    node = LiteralExpr(test_location, value=42, type_hint="int")

    class TestVisitor:
        def visit_LiteralExpr(self, node):
            return f"Visited literal: {node.value}"

    visitor = TestVisitor()
    result = node.accept(visitor)
    assert result == "Visited literal: 42"


def test_visitor_pattern_not_implemented(test_location):
    """Test visitor pattern with missing method."""
    node = LiteralExpr(test_location, value=42, type_hint="int")

    class IncompleteVisitor:
        pass

    visitor = IncompleteVisitor()
    with pytest.raises(NotImplementedError) as excinfo:
        node.accept(visitor)
    assert "visit_LiteralExpr" in str(excinfo.value)


# ============================================================================
# Expression Node Tests
# ============================================================================

def test_literal_expr_integer(test_location):
    """Test integer literal expression."""
    node = LiteralExpr(test_location, value=42, type_hint="int")
    assert node.value == 42
    assert node.type_hint == "int"
    assert node.location == test_location


def test_literal_expr_float(test_location):
    """Test float literal expression."""
    node = LiteralExpr(test_location, value=3.14, type_hint="float")
    assert node.value == 3.14
    assert node.type_hint == "float"


def test_literal_expr_string(test_location):
    """Test string literal expression."""
    node = LiteralExpr(test_location, value="hello", type_hint="string")
    assert node.value == "hello"
    assert node.type_hint == "string"


def test_literal_expr_char(test_location):
    """Test character literal expression."""
    node = LiteralExpr(test_location, value='c', type_hint="char")
    assert node.value == 'c'
    assert node.type_hint == "char"


def test_literal_expr_bool_true(test_location):
    """Test boolean true literal expression."""
    node = LiteralExpr(test_location, value=True, type_hint="bool")
    assert node.value is True
    assert node.type_hint == "bool"


def test_literal_expr_bool_false(test_location):
    """Test boolean false literal expression."""
    node = LiteralExpr(test_location, value=False, type_hint="bool")
    assert node.value is False
    assert node.type_hint == "bool"


def test_literal_expr_null(test_location):
    """Test null literal expression."""
    node = LiteralExpr(test_location, value=None, type_hint="null")
    assert node.value is None
    assert node.type_hint == "null"


def test_identifier_expr(test_location):
    """Test identifier expression."""
    node = IdentifierExpr(test_location, name="my_variable")
    assert node.name == "my_variable"
    assert node.location == test_location


def test_binary_expr_addition(test_location):
    """Test binary addition expression."""
    left = LiteralExpr(test_location, value=5, type_hint="int")
    right = LiteralExpr(test_location, value=3, type_hint="int")
    node = BinaryExpr(test_location, left=left, operator="+", right=right)

    assert node.operator == "+"
    assert node.left.value == 5
    assert node.right.value == 3


def test_binary_expr_comparison(test_location):
    """Test binary comparison expression."""
    left = IdentifierExpr(test_location, name="x")
    right = LiteralExpr(test_location, value=10, type_hint="int")
    node = BinaryExpr(test_location, left=left, operator="<", right=right)

    assert node.operator == "<"
    assert node.left.name == "x"
    assert node.right.value == 10


def test_binary_expr_logical_and(test_location):
    """Test binary logical AND expression."""
    left = IdentifierExpr(test_location, name="a")
    right = IdentifierExpr(test_location, name="b")
    node = BinaryExpr(test_location, left=left, operator="and", right=right)

    assert node.operator == "and"
    assert node.left.name == "a"
    assert node.right.name == "b"


def test_unary_expr_negation(test_location):
    """Test unary negation expression."""
    operand = LiteralExpr(test_location, value=5, type_hint="int")
    node = UnaryExpr(test_location, operator="-", operand=operand)

    assert node.operator == "-"
    assert node.operand.value == 5


def test_unary_expr_not(test_location):
    """Test unary NOT expression."""
    operand = IdentifierExpr(test_location, name="flag")
    node = UnaryExpr(test_location, operator="not", operand=operand)

    assert node.operator == "not"
    assert node.operand.name == "flag"


def test_call_expr_no_args(test_location):
    """Test function call with no arguments."""
    callee = IdentifierExpr(test_location, name="get_value")
    node = CallExpr(test_location, callee=callee, arguments=[])

    assert node.callee.name == "get_value"
    assert len(node.arguments) == 0


def test_call_expr_with_args(test_location):
    """Test function call with arguments."""
    callee = IdentifierExpr(test_location, name="add")
    arg1 = LiteralExpr(test_location, value=5, type_hint="int")
    arg2 = LiteralExpr(test_location, value=3, type_hint="int")
    node = CallExpr(test_location, callee=callee, arguments=[arg1, arg2])

    assert node.callee.name == "add"
    assert len(node.arguments) == 2
    assert node.arguments[0].value == 5
    assert node.arguments[1].value == 3


def test_lambda_expr_simple(test_location):
    """Test simple lambda expression."""
    param1 = ParameterDecl(
        test_location,
        param_type=PrimitiveType(test_location, name="int"),
        name="x",
        default_value=None
    )
    param2 = ParameterDecl(
        test_location,
        param_type=PrimitiveType(test_location, name="int"),
        name="y",
        default_value=None
    )
    return_type = PrimitiveType(test_location, name="int")
    body = BinaryExpr(
        test_location,
        left=IdentifierExpr(test_location, name="x"),
        operator="+",
        right=IdentifierExpr(test_location, name="y")
    )

    node = LambdaExpr(
        test_location,
        parameters=[param1, param2],
        return_type=return_type,
        body=body
    )

    assert len(node.parameters) == 2
    assert node.parameters[0].name == "x"
    assert node.parameters[1].name == "y"
    assert node.return_type.name == "int"
    assert isinstance(node.body, BinaryExpr)


def test_interpolated_string_expr_inline(test_location):
    """Test interpolated string with inline variables."""
    # "Hello {name}, you are {age} years old"
    segments = [
        StringTextPart(text="Hello "),
        StringExprPart(expression=IdentifierExpr(test_location, name="name")),
        StringTextPart(text=", you are "),
        StringExprPart(expression=IdentifierExpr(test_location, name="age")),
        StringTextPart(text=" years old"),
    ]

    node = InterpolatedStringExpr(test_location, segments=segments)

    text_segments = [s for s in node.segments if isinstance(s, StringTextPart)]
    expr_segments = [s for s in node.segments if isinstance(s, StringExprPart)]
    assert len(text_segments) == 3
    assert text_segments[0].text == "Hello "
    assert len(expr_segments) == 2
    assert expr_segments[0].expression.name == "name"
    assert expr_segments[1].expression.name == "age"


def test_interpolated_string_expr_positional(test_location):
    """Test interpolated string with positional arguments."""
    # "User {@1} is {@2} years old"
    segments = [
        StringTextPart(text="User "),
        StringExprPart(expression=IdentifierExpr(test_location, name="name")),
        StringTextPart(text=" is "),
        StringExprPart(expression=IdentifierExpr(test_location, name="age")),
        StringTextPart(text=" years old"),
    ]

    node = InterpolatedStringExpr(test_location, segments=segments)

    text_segments = [s for s in node.segments if isinstance(s, StringTextPart)]
    expr_segments = [s for s in node.segments if isinstance(s, StringExprPart)]
    assert len(text_segments) == 3
    assert len(expr_segments) == 2


# ============================================================================
# Statement Node Tests
# ============================================================================

def test_expression_stmt(test_location):
    """Test expression statement."""
    expr = CallExpr(
        test_location,
        callee=IdentifierExpr(test_location, name="print"),
        arguments=[LiteralExpr(test_location, value="hello", type_hint="string")]
    )
    node = ExpressionStmt(test_location, expression=expr)

    assert isinstance(node.expression, CallExpr)
    assert node.expression.callee.name == "print"


def test_var_decl_stmt_with_init(test_location):
    """Test variable declaration with initializer."""
    var_type = PrimitiveType(test_location, name="int")
    initializer = LiteralExpr(test_location, value=42, type_hint="int")
    node = VarDeclStmt(
        test_location,
        var_type=var_type,
        name="count",
        initializer=initializer
    )

    assert node.var_type.name == "int"
    assert node.name == "count"
    assert node.initializer.value == 42


def test_var_decl_stmt_no_init(test_location):
    """Test variable declaration without initializer."""
    var_type = PrimitiveType(test_location, name="string")
    node = VarDeclStmt(
        test_location,
        var_type=var_type,
        name="name",
        initializer=None
    )

    assert node.var_type.name == "string"
    assert node.name == "name"
    assert node.initializer is None


def test_assignment_stmt(test_location):
    """Test assignment statement."""
    target = IdentifierExpr(test_location, name="x")
    value = LiteralExpr(test_location, value=10, type_hint="int")
    node = AssignmentStmt(test_location, target=target, value=value)

    assert node.target.name == "x"
    assert node.value.value == 10


def test_if_stmt_no_else(test_location):
    """Test if statement without else."""
    condition = BinaryExpr(
        test_location,
        left=IdentifierExpr(test_location, name="x"),
        operator=">",
        right=LiteralExpr(test_location, value=0, type_hint="int")
    )
    then_branch = BlockStmt(test_location, statements=[])

    node = IfStmt(
        test_location,
        condition=condition,
        then_branch=then_branch,
        else_branch=None
    )

    assert isinstance(node.condition, BinaryExpr)
    assert isinstance(node.then_branch, BlockStmt)
    assert node.else_branch is None


def test_if_stmt_with_else(test_location):
    """Test if statement with else."""
    condition = IdentifierExpr(test_location, name="flag")
    then_branch = BlockStmt(test_location, statements=[])
    else_branch = BlockStmt(test_location, statements=[])

    node = IfStmt(
        test_location,
        condition=condition,
        then_branch=then_branch,
        else_branch=else_branch
    )

    assert isinstance(node.condition, IdentifierExpr)
    assert isinstance(node.then_branch, BlockStmt)
    assert isinstance(node.else_branch, BlockStmt)


def test_while_stmt(test_location):
    """Test while statement."""
    condition = BinaryExpr(
        test_location,
        left=IdentifierExpr(test_location, name="i"),
        operator="<",
        right=LiteralExpr(test_location, value=10, type_hint="int")
    )
    body = BlockStmt(test_location, statements=[])

    node = WhileStmt(test_location, condition=condition, body=body)

    assert isinstance(node.condition, BinaryExpr)
    assert isinstance(node.body, BlockStmt)


def test_for_stmt(test_location):
    """Test for statement."""
    iterable = IdentifierExpr(test_location, name="items")
    body = BlockStmt(test_location, statements=[])

    node = ForStmt(
        test_location,
        variable="item",
        iterable=iterable,
        body=body
    )

    assert node.variable == "item"
    assert isinstance(node.iterable, IdentifierExpr)
    assert isinstance(node.body, BlockStmt)


def test_return_stmt_with_value(test_location):
    """Test return statement with value."""
    value = LiteralExpr(test_location, value=42, type_hint="int")
    node = ReturnStmt(test_location, value=value)

    assert node.value.value == 42


def test_return_stmt_void(test_location):
    """Test return statement without value (void)."""
    node = ReturnStmt(test_location, value=None)

    assert node.value is None


def test_block_stmt_empty(test_location):
    """Test empty block statement."""
    node = BlockStmt(test_location, statements=[])

    assert len(node.statements) == 0


def test_block_stmt_multiple_statements(test_location):
    """Test block statement with multiple statements."""
    stmt1 = VarDeclStmt(
        test_location,
        var_type=PrimitiveType(test_location, name="int"),
        name="x",
        initializer=LiteralExpr(test_location, value=5, type_hint="int")
    )
    stmt2 = AssignmentStmt(
        test_location,
        target=IdentifierExpr(test_location, name="x"),
        value=LiteralExpr(test_location, value=10, type_hint="int")
    )
    stmt3 = ReturnStmt(
        test_location,
        value=IdentifierExpr(test_location, name="x")
    )

    node = BlockStmt(test_location, statements=[stmt1, stmt2, stmt3])

    assert len(node.statements) == 3
    assert isinstance(node.statements[0], VarDeclStmt)
    assert isinstance(node.statements[1], AssignmentStmt)
    assert isinstance(node.statements[2], ReturnStmt)


# ============================================================================
# Declaration Node Tests
# ============================================================================

def test_parameter_decl_no_default(test_location):
    """Test parameter declaration without default value."""
    param_type = PrimitiveType(test_location, name="int")
    node = ParameterDecl(
        test_location,
        param_type=param_type,
        name="x",
        default_value=None
    )

    assert node.param_type.name == "int"
    assert node.name == "x"
    assert node.default_value is None


def test_parameter_decl_with_default(test_location):
    """Test parameter declaration with default value."""
    param_type = PrimitiveType(test_location, name="int")
    default = LiteralExpr(test_location, value=0, type_hint="int")
    node = ParameterDecl(
        test_location,
        param_type=param_type,
        name="count",
        default_value=default
    )

    assert node.param_type.name == "int"
    assert node.name == "count"
    assert node.default_value.value == 0


def test_function_decl_simple(test_location):
    """Test simple function declaration."""
    return_type = PrimitiveType(test_location, name="int")
    param1 = ParameterDecl(
        test_location,
        param_type=PrimitiveType(test_location, name="int"),
        name="a",
        default_value=None
    )
    param2 = ParameterDecl(
        test_location,
        param_type=PrimitiveType(test_location, name="int"),
        name="b",
        default_value=None
    )
    body = BlockStmt(
        test_location,
        statements=[
            ReturnStmt(
                test_location,
                value=BinaryExpr(
                    test_location,
                    left=IdentifierExpr(test_location, name="a"),
                    operator="+",
                    right=IdentifierExpr(test_location, name="b")
                )
            )
        ]
    )

    node = FunctionDecl(
        test_location,
        return_type=return_type,
        name="add",
        parameters=[param1, param2],
        body=body,
        is_lambda=False
    )

    assert node.return_type.name == "int"
    assert node.name == "add"
    assert len(node.parameters) == 2
    assert node.parameters[0].name == "a"
    assert node.parameters[1].name == "b"
    assert isinstance(node.body, BlockStmt)
    assert node.is_lambda is False


def test_function_decl_lambda(test_location):
    """Test inline lambda function declaration."""
    return_type = PrimitiveType(test_location, name="int")
    param = ParameterDecl(
        test_location,
        param_type=PrimitiveType(test_location, name="int"),
        name="x",
        default_value=None
    )
    body = BinaryExpr(
        test_location,
        left=IdentifierExpr(test_location, name="x"),
        operator="*",
        right=LiteralExpr(test_location, value=2, type_hint="int")
    )

    node = FunctionDecl(
        test_location,
        return_type=return_type,
        name="double",
        parameters=[param],
        body=body,
        is_lambda=True
    )

    assert node.name == "double"
    assert node.is_lambda is True
    assert isinstance(node.body, BinaryExpr)


def test_function_decl_no_params(test_location):
    """Test function declaration with no parameters."""
    return_type = PrimitiveType(test_location, name="void")
    body = BlockStmt(test_location, statements=[])

    node = FunctionDecl(
        test_location,
        return_type=return_type,
        name="hello",
        parameters=[],
        body=body
    )

    assert node.name == "hello"
    assert len(node.parameters) == 0
    assert node.return_type.name == "void"


def test_program_node_empty(test_location):
    """Test empty program node."""
    node = ProgramNode(test_location, declarations=[])

    assert len(node.declarations) == 0


def test_program_node_with_declarations(test_location):
    """Test program node with declarations."""
    func1 = FunctionDecl(
        test_location,
        return_type=PrimitiveType(test_location, name="void"),
        name="main",
        parameters=[],
        body=BlockStmt(test_location, statements=[])
    )
    var1 = VarDeclStmt(
        test_location,
        var_type=PrimitiveType(test_location, name="int"),
        name="global_var",
        initializer=LiteralExpr(test_location, value=100, type_hint="int")
    )

    node = ProgramNode(test_location, declarations=[func1, var1])

    assert len(node.declarations) == 2
    assert isinstance(node.declarations[0], FunctionDecl)
    assert isinstance(node.declarations[1], VarDeclStmt)


# ============================================================================
# Type Node Tests
# ============================================================================

def test_primitive_type_int(test_location):
    """Test int primitive type."""
    node = PrimitiveType(test_location, name="int")

    assert node.name == "int"
    assert isinstance(node, TypeNode)


def test_primitive_type_float(test_location):
    """Test float primitive type."""
    node = PrimitiveType(test_location, name="float")

    assert node.name == "float"


def test_primitive_type_string(test_location):
    """Test string primitive type."""
    node = PrimitiveType(test_location, name="string")

    assert node.name == "string"


def test_primitive_type_bool(test_location):
    """Test bool primitive type."""
    node = PrimitiveType(test_location, name="bool")

    assert node.name == "bool"


def test_primitive_type_char(test_location):
    """Test char primitive type."""
    node = PrimitiveType(test_location, name="char")

    assert node.name == "char"


def test_primitive_type_void(test_location):
    """Test void primitive type."""
    node = PrimitiveType(test_location, name="void")

    assert node.name == "void"


def test_function_type_simple(test_location):
    """Test simple function type."""
    param_types = [
        PrimitiveType(test_location, name="int"),
        PrimitiveType(test_location, name="int")
    ]
    return_type = PrimitiveType(test_location, name="int")

    node = FunctionType(
        test_location,
        parameter_types=param_types,
        return_type=return_type
    )

    assert len(node.parameter_types) == 2
    assert node.parameter_types[0].name == "int"
    assert node.parameter_types[1].name == "int"
    assert node.return_type.name == "int"


def test_function_type_no_params(test_location):
    """Test function type with no parameters."""
    return_type = PrimitiveType(test_location, name="void")

    node = FunctionType(
        test_location,
        parameter_types=[],
        return_type=return_type
    )

    assert len(node.parameter_types) == 0
    assert node.return_type.name == "void"


# ============================================================================
# Visitor Pattern Tests
# ============================================================================

def test_visitor_all_expression_nodes(test_location):
    """Test visitor pattern on all expression node types."""
    class ExpressionCounter:
        def __init__(self):
            self.count = 0

        def visit_LiteralExpr(self, node):
            self.count += 1
            return "literal"

        def visit_IdentifierExpr(self, node):
            self.count += 1
            return "identifier"

        def visit_BinaryExpr(self, node):
            self.count += 1
            return "binary"

        def visit_UnaryExpr(self, node):
            self.count += 1
            return "unary"

        def visit_CallExpr(self, node):
            self.count += 1
            return "call"

    visitor = ExpressionCounter()

    # Test each expression type
    LiteralExpr(test_location, value=1, type_hint="int").accept(visitor)
    IdentifierExpr(test_location, name="x").accept(visitor)
    BinaryExpr(
        test_location,
        left=IdentifierExpr(test_location, name="a"),
        operator="+",
        right=IdentifierExpr(test_location, name="b")
    ).accept(visitor)
    UnaryExpr(
        test_location,
        operator="-",
        operand=LiteralExpr(test_location, value=5, type_hint="int")
    ).accept(visitor)
    CallExpr(
        test_location,
        callee=IdentifierExpr(test_location, name="func"),
        arguments=[]
    ).accept(visitor)

    assert visitor.count == 5


def test_visitor_all_statement_nodes(test_location):
    """Test visitor pattern on all statement node types."""
    class StatementCounter:
        def __init__(self):
            self.count = 0

        def visit_ExpressionStmt(self, node):
            self.count += 1

        def visit_VarDeclStmt(self, node):
            self.count += 1

        def visit_AssignmentStmt(self, node):
            self.count += 1

        def visit_IfStmt(self, node):
            self.count += 1

        def visit_WhileStmt(self, node):
            self.count += 1

        def visit_ForStmt(self, node):
            self.count += 1

        def visit_ReturnStmt(self, node):
            self.count += 1

        def visit_BlockStmt(self, node):
            self.count += 1

    visitor = StatementCounter()

    # Test each statement type
    ExpressionStmt(
        test_location,
        expression=LiteralExpr(test_location, value=1, type_hint="int")
    ).accept(visitor)

    VarDeclStmt(
        test_location,
        var_type=PrimitiveType(test_location, name="int"),
        name="x",
        initializer=None
    ).accept(visitor)

    AssignmentStmt(
        test_location,
        target=IdentifierExpr(test_location, name="x"),
        value=LiteralExpr(test_location, value=5, type_hint="int")
    ).accept(visitor)

    IfStmt(
        test_location,
        condition=IdentifierExpr(test_location, name="flag"),
        then_branch=BlockStmt(test_location, statements=[]),
        else_branch=None
    ).accept(visitor)

    WhileStmt(
        test_location,
        condition=IdentifierExpr(test_location, name="flag"),
        body=BlockStmt(test_location, statements=[])
    ).accept(visitor)

    ForStmt(
        test_location,
        variable="i",
        iterable=IdentifierExpr(test_location, name="items"),
        body=BlockStmt(test_location, statements=[])
    ).accept(visitor)

    ReturnStmt(test_location, value=None).accept(visitor)
    BlockStmt(test_location, statements=[]).accept(visitor)

    assert visitor.count == 8


# ============================================================================
# Node Representation Tests
# ============================================================================

def test_literal_expr_repr(test_location):
    """Test LiteralExpr __repr__ method."""
    node = LiteralExpr(test_location, value=42, type_hint="int")
    repr_str = repr(node)

    assert "LiteralExpr" in repr_str
    assert "42" in repr_str
    assert "int" in repr_str


def test_binary_expr_repr(test_location):
    """Test BinaryExpr __repr__ method."""
    left = LiteralExpr(test_location, value=5, type_hint="int")
    right = LiteralExpr(test_location, value=3, type_hint="int")
    node = BinaryExpr(test_location, left=left, operator="+", right=right)
    repr_str = repr(node)

    assert "BinaryExpr" in repr_str
    assert "+" in repr_str


def test_function_decl_repr(test_location):
    """Test FunctionDecl __repr__ method."""
    node = FunctionDecl(
        test_location,
        return_type=PrimitiveType(test_location, name="int"),
        name="add",
        parameters=[],
        body=BlockStmt(test_location, statements=[])
    )
    repr_str = repr(node)

    assert "FunctionDecl" in repr_str
    assert "add" in repr_str
