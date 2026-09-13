"""Tests for the name resolver."""

import pytest
from src.semantic.name_resolver import NameResolver
from src.semantic.symbol_table import SymbolTable
from src.semantic.errors import SemanticError
from src.parser.ast_nodes import (
    ProgramNode, FunctionDecl, ParameterDecl,
    VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, BlockStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr, CallExpr, LambdaExpr,
    PrimitiveType, FunctionType
)
from src.lexer.token import SourceLocation


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def symbol_table():
    """Create an empty symbol table."""
    return SymbolTable()


@pytest.fixture
def name_resolver(symbol_table):
    """Create a name resolver with symbol table."""
    return NameResolver(symbol_table)


@pytest.fixture
def location():
    """Create a dummy source location."""
    return SourceLocation("test.fusion", 1, 1)


# ============================================================================
# Function Registration Tests (8 tests)
# ============================================================================

def test_register_single_function(name_resolver, location):
    """Test registering a single function."""
    int_type = PrimitiveType(location=location, name='int')
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0
    assert name_resolver.symbol_table.lookup('test') is not None


def test_register_multiple_functions(name_resolver, location):
    """Test registering multiple functions."""
    int_type = PrimitiveType(location=location, name='int')
    body = BlockStmt(statements=[], location=location)

    func1 = FunctionDecl(
        return_type=int_type,
        name='func1',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    func2 = FunctionDecl(
        return_type=int_type,
        name='func2',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func1, func2], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0
    assert name_resolver.symbol_table.lookup('func1') is not None
    assert name_resolver.symbol_table.lookup('func2') is not None


def test_duplicate_function_name_error(name_resolver, location):
    """Test error for duplicate function name."""
    int_type = PrimitiveType(location=location, name='int')
    body = BlockStmt(statements=[], location=location)

    func1 = FunctionDecl(
        return_type=int_type,
        name='duplicate',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    func2 = FunctionDecl(
        return_type=int_type,
        name='duplicate',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func1, func2], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "duplicate" in errors[0].message.lower()


def test_function_with_parameters(name_resolver, location):
    """Test registering function with parameters."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0
    symbol = name_resolver.symbol_table.lookup('test')
    assert symbol is not None
    assert isinstance(symbol.data_type, FunctionType)
    assert len(symbol.data_type.parameter_types) == 1


def test_function_with_return_type(name_resolver, location):
    """Test function with return type."""
    string_type = PrimitiveType(location=location, name='string')
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=string_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0
    symbol = name_resolver.symbol_table.lookup('test')
    assert isinstance(symbol.data_type, FunctionType)
    assert symbol.data_type.return_type.name == 'string'


def test_empty_function(name_resolver, location):
    """Test empty function."""
    void_type = PrimitiveType(location=location, name='void')
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=void_type,
        name='empty',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_builtin_print_function(name_resolver):
    """Test that print function is registered as built-in."""
    symbol = name_resolver.symbol_table.lookup('print')
    assert symbol is not None
    assert symbol.symbol_type == 'function'


def test_forward_reference(name_resolver, location):
    """Test forward reference (call function before definition in source)."""
    int_type = PrimitiveType(location=location, name='int')

    # Function that calls another function
    call_expr = CallExpr(
        callee=IdentifierExpr(name='helper', location=location),
        arguments=[],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=call_expr, location=location)
    caller_body = BlockStmt(statements=[expr_stmt], location=location)

    caller = FunctionDecl(
        return_type=int_type,
        name='caller',
        parameters=[],
        body=caller_body,
        is_lambda=False,
        location=location
    )

    # Helper function defined after caller
    helper_body = BlockStmt(statements=[], location=location)
    helper = FunctionDecl(
        return_type=int_type,
        name='helper',
        parameters=[],
        body=helper_body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[caller, helper], location=location)
    errors = name_resolver.resolve_program(program)

    # Should have no errors because two-pass resolution registers all functions first
    assert len(errors) == 0


# ============================================================================
# Parameter Resolution Tests (6 tests)
# ============================================================================

def test_register_single_parameter(name_resolver, symbol_table, location):
    """Test registering a single parameter."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_register_multiple_parameters(name_resolver, location):
    """Test registering multiple parameters."""
    int_type = PrimitiveType(location=location, name='int')
    param1 = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    param2 = ParameterDecl(param_type=int_type, name='y', default_value=None, location=location)
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='add',
        parameters=[param1, param2],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_duplicate_parameter_name_error(name_resolver, location):
    """Test error for duplicate parameter name."""
    int_type = PrimitiveType(location=location, name='int')
    param1 = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    param2 = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[param1, param2],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "duplicate" in errors[0].message.lower() or "x" in errors[0].message


def test_parameter_visible_in_function_body(name_resolver, location):
    """Test parameter is visible in function body."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)

    # Function body that uses the parameter
    ident = IdentifierExpr(name='x', location=location)
    return_stmt = ReturnStmt(value=ident, location=location)
    body = BlockStmt(statements=[return_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='identity',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_parameter_not_visible_outside_function(name_resolver, location):
    """Test parameter is not visible outside function."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # After resolution, parameter should not be in global scope
    symbol = name_resolver.symbol_table.lookup('x')
    assert symbol is None


def test_parameter_shadows_global_variable(name_resolver, location):
    """Test parameter can shadow global variable."""
    int_type = PrimitiveType(location=location, name='int')

    # Global variable x
    global_var = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=10, type_hint='int', location=location),
        location=location
    )

    # Function with parameter x
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    ident = IdentifierExpr(name='x', location=location)
    return_stmt = ReturnStmt(value=ident, location=location)
    body = BlockStmt(statements=[return_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[global_var, func], location=location)
    errors = name_resolver.resolve_program(program)

    # Shadowing is allowed, no errors
    assert len(errors) == 0


# ============================================================================
# Variable Resolution Tests (10 tests)
# ============================================================================

def test_define_variable_in_function(name_resolver, location):
    """Test defining a variable in a function."""
    int_type = PrimitiveType(location=location, name='int')

    var_decl = VarDeclStmt(
        var_type=int_type,
        name='y',
        initializer=LiteralExpr(value=5, type_hint='int', location=location),
        location=location
    )
    body = BlockStmt(statements=[var_decl], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_use_variable_after_definition(name_resolver, location):
    """Test using a variable after definition."""
    int_type = PrimitiveType(location=location, name='int')

    var_decl = VarDeclStmt(
        var_type=int_type,
        name='y',
        initializer=LiteralExpr(value=5, type_hint='int', location=location),
        location=location
    )
    use_stmt = ReturnStmt(value=IdentifierExpr(name='y', location=location), location=location)
    body = BlockStmt(statements=[var_decl, use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_use_variable_before_definition_error(name_resolver, location):
    """Test error when using variable before definition."""
    int_type = PrimitiveType(location=location, name='int')

    # Use variable before defining it
    use_stmt = ReturnStmt(value=IdentifierExpr(name='y', location=location), location=location)
    var_decl = VarDeclStmt(
        var_type=int_type,
        name='y',
        initializer=LiteralExpr(value=5, type_hint='int', location=location),
        location=location
    )
    body = BlockStmt(statements=[use_stmt, var_decl], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "undefined" in errors[0].message.lower()


def test_duplicate_variable_in_same_scope_error(name_resolver, location):
    """Test error for duplicate variable in same scope."""
    int_type = PrimitiveType(location=location, name='int')

    var1 = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )
    var2 = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=2, type_hint='int', location=location),
        location=location
    )
    body = BlockStmt(statements=[var1, var2], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "duplicate" in errors[0].message.lower() or "x" in errors[0].message


def test_variable_in_nested_scope(name_resolver, location):
    """Test variable in nested scope."""
    int_type = PrimitiveType(location=location, name='int')

    # Inner block with variable
    inner_var = VarDeclStmt(
        var_type=int_type,
        name='inner',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )
    inner_block = BlockStmt(statements=[inner_var], location=location)

    body = BlockStmt(statements=[inner_block], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_inner_scope_shadows_outer_scope(name_resolver, location):
    """Test block scoping (Task 12.6): redeclaring a name in a nested block shadows the
    outer variable rather than erroring - each block has its own scope."""
    int_type = PrimitiveType(location=location, name='int')

    # Outer variable
    outer_var = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )

    # Inner variable with same name - shadows the outer one, no error under block scoping
    inner_var = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=2, type_hint='int', location=location),
        location=location
    )
    inner_block = BlockStmt(statements=[inner_var], location=location)

    body = BlockStmt(statements=[outer_var, inner_block], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Block scoping: shadowing in a nested block is allowed
    assert len(errors) == 0


def test_variable_not_visible_outside_scope(name_resolver, location):
    """Test block scoping (Task 12.6): a variable declared inside a nested block is NOT
    visible after that block ends - matches what the generated C code already enforces
    via its own { } braces (this was a real bug under the old function-scoping model:
    semantic analysis allowed it, but the resulting C failed to compile)."""
    int_type = PrimitiveType(location=location, name='int')

    # Variable defined in inner block
    inner_var = VarDeclStmt(
        var_type=int_type,
        name='inner',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )
    inner_block = BlockStmt(statements=[inner_var], location=location)

    # Try to use it outside the block - now an error under block scoping
    use_stmt = ReturnStmt(value=IdentifierExpr(name='inner', location=location), location=location)

    body = BlockStmt(statements=[inner_block, use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Block scoping: 'inner' went out of scope when its block ended
    assert len(errors) == 1
    assert "undefined" in errors[0].message.lower()


def test_multiple_variables_in_scope(name_resolver, location):
    """Test multiple variables in same scope."""
    int_type = PrimitiveType(location=location, name='int')

    var1 = VarDeclStmt(
        var_type=int_type,
        name='a',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )
    var2 = VarDeclStmt(
        var_type=int_type,
        name='b',
        initializer=LiteralExpr(value=2, type_hint='int', location=location),
        location=location
    )
    var3 = VarDeclStmt(
        var_type=int_type,
        name='c',
        initializer=LiteralExpr(value=3, type_hint='int', location=location),
        location=location
    )
    body = BlockStmt(statements=[var1, var2, var3], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_variable_in_loop_scope(name_resolver, location):
    """Test variable in for loop scope."""
    int_type = PrimitiveType(location=location, name='int')

    # For loop with body
    loop_body = BlockStmt(statements=[], location=location)
    for_stmt = ForStmt(
        variable='i',
        iterable=LiteralExpr(value=10, type_hint='int', location=location),
        body=loop_body,
        location=location
    )

    body = BlockStmt(statements=[for_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_global_variable_declaration(name_resolver, location):
    """Test global variable declaration."""
    int_type = PrimitiveType(location=location, name='int')

    global_var = VarDeclStmt(
        var_type=int_type,
        name='global_x',
        initializer=LiteralExpr(value=100, type_hint='int', location=location),
        location=location
    )

    program = ProgramNode(declarations=[global_var], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0
    symbol = name_resolver.symbol_table.lookup('global_x')
    assert symbol is not None
    assert symbol.symbol_type == 'variable'


# ============================================================================
# Identifier Resolution Tests (8 tests)
# ============================================================================

def test_resolve_local_variable(name_resolver, location):
    """Test resolving local variable."""
    int_type = PrimitiveType(location=location, name='int')

    var_decl = VarDeclStmt(
        var_type=int_type,
        name='local',
        initializer=LiteralExpr(value=5, type_hint='int', location=location),
        location=location
    )
    use_stmt = ReturnStmt(value=IdentifierExpr(name='local', location=location), location=location)
    body = BlockStmt(statements=[var_decl, use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_resolve_parameter(name_resolver, location):
    """Test resolving parameter."""
    int_type = PrimitiveType(location=location, name='int')
    param = ParameterDecl(param_type=int_type, name='p', default_value=None, location=location)

    use_stmt = ReturnStmt(value=IdentifierExpr(name='p', location=location), location=location)
    body = BlockStmt(statements=[use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[param],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_resolve_variable_from_parent_scope(name_resolver, location):
    """Test resolving variable from parent scope."""
    int_type = PrimitiveType(location=location, name='int')

    # Outer variable
    outer_var = VarDeclStmt(
        var_type=int_type,
        name='outer',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )

    # Inner block uses outer variable
    use_stmt = ReturnStmt(value=IdentifierExpr(name='outer', location=location), location=location)
    inner_block = BlockStmt(statements=[use_stmt], location=location)

    body = BlockStmt(statements=[outer_var, inner_block], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_undefined_variable_error(name_resolver, location):
    """Test error for undefined variable."""
    int_type = PrimitiveType(location=location, name='int')

    use_stmt = ReturnStmt(value=IdentifierExpr(name='undefined', location=location), location=location)
    body = BlockStmt(statements=[use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "undefined" in errors[0].message.lower()


def test_resolve_after_multiple_scopes(name_resolver, location):
    """Test resolving through multiple scope levels."""
    int_type = PrimitiveType(location=location, name='int')

    # Level 1: function scope variable
    level1_var = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )

    # Level 2: inner block
    level2_block = BlockStmt(statements=[], location=location)

    # Level 3: even more nested block that uses x
    use_stmt = ReturnStmt(value=IdentifierExpr(name='x', location=location), location=location)
    level3_block = BlockStmt(statements=[use_stmt], location=location)

    level2_block.statements.append(level3_block)

    body = BlockStmt(statements=[level1_var, level2_block], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_shadowing_resolution_inner_wins(name_resolver, location):
    """Test block scoping (Task 12.6): an inner declaration shadowing an outer one
    resolves to the inner variable within its own block, with no error."""
    int_type = PrimitiveType(location=location, name='int')

    # Outer variable
    outer_var = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )

    # Inner variable shadows outer - allowed under block scoping
    inner_var = VarDeclStmt(
        var_type=int_type,
        name='x',
        initializer=LiteralExpr(value=2, type_hint='int', location=location),
        location=location
    )
    # Use x - resolves to the inner (shadowing) declaration
    use_stmt = ReturnStmt(value=IdentifierExpr(name='x', location=location), location=location)
    inner_block = BlockStmt(statements=[inner_var, use_stmt], location=location)

    body = BlockStmt(statements=[outer_var, inner_block], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Block scoping: shadowing is allowed, no error
    assert len(errors) == 0


def test_global_variable_access_from_function(name_resolver, location):
    """Test accessing global variable from function."""
    int_type = PrimitiveType(location=location, name='int')

    # Global variable
    global_var = VarDeclStmt(
        var_type=int_type,
        name='global_x',
        initializer=LiteralExpr(value=100, type_hint='int', location=location),
        location=location
    )

    # Function that uses global variable
    use_stmt = ReturnStmt(value=IdentifierExpr(name='global_x', location=location), location=location)
    body = BlockStmt(statements=[use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[global_var, func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_variable_in_if_branch_not_visible_outside(name_resolver, location):
    """Test block scoping (Task 12.6): a variable declared inside an if branch is not
    visible after the if statement ends."""
    int_type = PrimitiveType(location=location, name='int')
    bool_type = PrimitiveType(location=location, name='bool')

    # Variable defined in if branch
    var_in_if = VarDeclStmt(
        var_type=int_type,
        name='if_var',
        initializer=LiteralExpr(value=1, type_hint='int', location=location),
        location=location
    )
    if_body = BlockStmt(statements=[var_in_if], location=location)

    if_stmt = IfStmt(
        condition=LiteralExpr(value=True, type_hint='bool', location=location),
        then_branch=if_body,
        else_branch=None,
        location=location
    )

    # Try to use it after if - an error under block scoping
    use_stmt = ReturnStmt(value=IdentifierExpr(name='if_var', location=location), location=location)

    body = BlockStmt(statements=[if_stmt, use_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Block scoping: if_var went out of scope when the if statement ended
    assert len(errors) == 1
    assert "undefined" in errors[0].message.lower()


# ============================================================================
# Function Call Resolution Tests (7 tests)
# ============================================================================

def test_call_defined_function(name_resolver, location):
    """Test calling a defined function."""
    int_type = PrimitiveType(location=location, name='int')

    # Define helper function
    helper_body = BlockStmt(statements=[], location=location)
    helper = FunctionDecl(
        return_type=int_type,
        name='helper',
        parameters=[],
        body=helper_body,
        is_lambda=False,
        location=location
    )

    # Call helper
    call_expr = CallExpr(
        callee=IdentifierExpr(name='helper', location=location),
        arguments=[],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=call_expr, location=location)
    caller_body = BlockStmt(statements=[expr_stmt], location=location)

    caller = FunctionDecl(
        return_type=int_type,
        name='caller',
        parameters=[],
        body=caller_body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[helper, caller], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_call_undefined_function_error(name_resolver, location):
    """Test error when calling undefined function."""
    int_type = PrimitiveType(location=location, name='int')

    call_expr = CallExpr(
        callee=IdentifierExpr(name='undefined_func', location=location),
        arguments=[],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=call_expr, location=location)
    body = BlockStmt(statements=[expr_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "undefined" in errors[0].message.lower()


def test_call_variable_as_function_error(name_resolver, location):
    """Test error when calling a variable as a function."""
    int_type = PrimitiveType(location=location, name='int')

    # Define variable
    var_decl = VarDeclStmt(
        var_type=int_type,
        name='not_a_func',
        initializer=LiteralExpr(value=5, type_hint='int', location=location),
        location=location
    )

    # Try to call it
    call_expr = CallExpr(
        callee=IdentifierExpr(name='not_a_func', location=location),
        arguments=[],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=call_expr, location=location)

    body = BlockStmt(statements=[var_decl, expr_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 1
    assert "not a function" in errors[0].message.lower()


def test_nested_function_calls(name_resolver, location):
    """Test nested function calls."""
    int_type = PrimitiveType(location=location, name='int')

    # Define inner function
    inner_body = BlockStmt(statements=[], location=location)
    inner_func = FunctionDecl(
        return_type=int_type,
        name='inner',
        parameters=[],
        body=inner_body,
        is_lambda=False,
        location=location
    )

    # Call inner() inside outer call: outer(inner())
    inner_call = CallExpr(
        callee=IdentifierExpr(name='inner', location=location),
        arguments=[],
        location=location
    )
    outer_call = CallExpr(
        callee=IdentifierExpr(name='print', location=location),  # Use builtin print
        arguments=[LiteralExpr(value="test", type_hint='string', location=location)],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=outer_call, location=location)

    caller_body = BlockStmt(statements=[expr_stmt], location=location)
    caller = FunctionDecl(
        return_type=int_type,
        name='caller',
        parameters=[],
        body=caller_body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[inner_func, caller], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_recursive_function_call(name_resolver, location):
    """Test recursive function call."""
    int_type = PrimitiveType(location=location, name='int')

    # Recursive call to self
    call_expr = CallExpr(
        callee=IdentifierExpr(name='recursive', location=location),
        arguments=[],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=call_expr, location=location)
    body = BlockStmt(statements=[expr_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='recursive',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Recursion is allowed
    assert len(errors) == 0


def test_call_builtin_print(name_resolver, location):
    """Test calling built-in print function."""
    void_type = PrimitiveType(location=location, name='void')

    call_expr = CallExpr(
        callee=IdentifierExpr(name='print', location=location),
        arguments=[LiteralExpr(value="Hello", type_hint='string', location=location)],
        location=location
    )
    expr_stmt = ExpressionStmt(expression=call_expr, location=location)
    body = BlockStmt(statements=[expr_stmt], location=location)

    func = FunctionDecl(
        return_type=void_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


# ============================================================================
# Scope Management Tests (6 tests)
# ============================================================================

def test_enter_exit_function_scope(name_resolver, location):
    """Test entering and exiting function scope."""
    int_type = PrimitiveType(location=location, name='int')
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Should be back in global scope
    assert name_resolver.symbol_table.get_scope_depth() == 0
    assert len(errors) == 0


def test_enter_exit_block_scope(name_resolver, location):
    """Test entering and exiting block scope."""
    int_type = PrimitiveType(location=location, name='int')

    inner_block = BlockStmt(statements=[], location=location)
    body = BlockStmt(statements=[inner_block], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_enter_exit_for_loop_scope(name_resolver, location):
    """Test entering and exiting for loop scope."""
    int_type = PrimitiveType(location=location, name='int')

    for_stmt = ForStmt(
        variable='i',
        iterable=LiteralExpr(value=10, type_hint='int', location=location),
        body=BlockStmt(statements=[], location=location),
        location=location
    )

    body = BlockStmt(statements=[for_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_nested_scopes_three_levels(name_resolver, location):
    """Test nested scopes (3+ levels)."""
    int_type = PrimitiveType(location=location, name='int')

    # Level 3
    level3 = BlockStmt(statements=[], location=location)
    # Level 2
    level2 = BlockStmt(statements=[level3], location=location)
    # Level 1 (function body)
    level1 = BlockStmt(statements=[level2], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=level1,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    assert len(errors) == 0


def test_lambda_scope_isolation(name_resolver, location):
    """Test lambda scope isolation."""
    int_type = PrimitiveType(location=location, name='int')

    # Lambda with parameter
    param = ParameterDecl(param_type=int_type, name='x', default_value=None, location=location)
    lambda_body = IdentifierExpr(name='x', location=location)

    lambda_expr = LambdaExpr(
        parameters=[param],
        return_type=int_type,
        body=lambda_body,
        location=location
    )

    # Use lambda in expression statement
    expr_stmt = ExpressionStmt(expression=lambda_expr, location=location)
    body = BlockStmt(statements=[expr_stmt], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    errors = name_resolver.resolve_program(program)

    # Lambda parameter should not leak to outer scope
    assert len(errors) == 0


def test_scope_cleanup_on_completion(name_resolver, location):
    """Test scope is properly cleaned up after resolution."""
    int_type = PrimitiveType(location=location, name='int')
    body = BlockStmt(statements=[], location=location)

    func = FunctionDecl(
        return_type=int_type,
        name='test',
        parameters=[],
        body=body,
        is_lambda=False,
        location=location
    )

    program = ProgramNode(declarations=[func], location=location)
    name_resolver.resolve_program(program)

    # Should be back at global scope (depth 0)
    assert name_resolver.symbol_table.get_scope_depth() == 0
