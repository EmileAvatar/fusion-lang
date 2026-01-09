"""Name resolution for the Fusion semantic analyzer.

This module implements name resolution to link identifier uses to their declarations,
validate scoping rules, and detect undefined variables/functions.
"""

from typing import Optional, List
from src.parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, BlockStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr, CallExpr, LambdaExpr,
    InterpolatedStringExpr,
    TypeNode, PrimitiveType, FunctionType
)
from .symbol_table import SymbolTable
from .symbol import Symbol
from .errors import SemanticError
from src.lexer.token import SourceLocation


class NameResolver:
    """Resolves names and populates the symbol table.

    Performs two-pass resolution:
    - Pass 1: Register all function declarations in global scope
    - Pass 2: Resolve function bodies (parameters, local variables, calls)

    Attributes:
        symbol_table: Symbol table for registering symbols
        errors: List of semantic errors found during resolution
        current_function: Name of currently resolving function (or None)
    """

    def __init__(self, symbol_table: SymbolTable):
        """Initialize name resolver.

        Args:
            symbol_table: Symbol table for symbol registration
        """
        self.symbol_table = symbol_table
        self.errors: List[SemanticError] = []
        self.current_function: Optional[str] = None

        # Register built-in functions
        self.register_builtins()

    def register_builtins(self) -> None:
        """Register built-in functions like print and range."""
        # print function: void print(string message)
        builtin_loc = SourceLocation('<builtin>', 0, 0)
        string_type = PrimitiveType(location=builtin_loc, name='string')
        void_type = PrimitiveType(location=builtin_loc, name='void')
        int_type = PrimitiveType(location=builtin_loc, name='int')

        print_type = FunctionType(
            parameter_types=[string_type],
            return_type=void_type,
            location=builtin_loc
        )

        print_symbol = Symbol(
            name='print',
            symbol_type='function',
            data_type=print_type,
            location=builtin_loc
        )

        try:
            self.symbol_table.define(print_symbol)
        except SemanticError:
            # Ignore if already defined (shouldn't happen)
            pass

        # range function: int range(int start, int end) or range(int start, int end, int step)
        # For simplicity, we'll register it as a variadic function with int return type
        # The actual implementation is handled during code generation
        range_type = FunctionType(
            parameter_types=[int_type, int_type, int_type],  # start, end, step
            return_type=int_type,
            location=builtin_loc
        )

        range_symbol = Symbol(
            name='range',
            symbol_type='function',
            data_type=range_type,
            location=builtin_loc
        )

        try:
            self.symbol_table.define(range_symbol)
        except SemanticError:
            # Ignore if already defined (shouldn't happen)
            pass

    def resolve_program(self, program: ProgramNode) -> List[SemanticError]:
        """Resolve all names in the program (two-pass).

        Args:
            program: Root AST node

        Returns:
            List of semantic errors found (empty if no errors)
        """
        self.errors = []  # Reset errors

        # Pass 1: Register all function declarations
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.register_function(decl)

        # Pass 2: Resolve function bodies
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.resolve_function(decl)
            elif isinstance(decl, VarDeclStmt):
                # Global variable declaration
                self.resolve_var_decl(decl)

        return self.errors

    # ========================================================================
    # Pass 1: Function Registration
    # ========================================================================

    def register_function(self, func: FunctionDecl) -> None:
        """Register a function in the global symbol table.

        Args:
            func: Function declaration node
        """
        try:
            # Create function type
            param_types = [param.param_type for param in func.parameters]
            func_type = FunctionType(
                parameter_types=param_types,
                return_type=func.return_type,
                location=func.location
            )

            # Create symbol
            symbol = Symbol(
                name=func.name,
                symbol_type='function',
                data_type=func_type,
                location=func.location
            )

            # Add to global scope
            self.symbol_table.define(symbol)

        except SemanticError as e:
            self.errors.append(e)

    # ========================================================================
    # Pass 2: Function Body Resolution
    # ========================================================================

    def resolve_function(self, func: FunctionDecl) -> None:
        """Resolve names inside a function body.

        Args:
            func: Function declaration node
        """
        self.current_function = func.name

        # Enter function scope
        self.symbol_table.enter_scope(f"function:{func.name}")

        try:
            # Register parameters
            for param in func.parameters:
                self.register_parameter(param)

            # Resolve function body
            if func.body:
                self.resolve_statement(func.body)

        finally:
            # Always exit scope, even on error
            try:
                self.symbol_table.exit_scope()
            except SemanticError:
                pass  # Scope already exited
            self.current_function = None

    def register_parameter(self, param: ParameterDecl) -> None:
        """Register a function parameter in current scope.

        Args:
            param: Parameter declaration node
        """
        try:
            symbol = Symbol(
                name=param.name,
                symbol_type='parameter',
                data_type=param.param_type,
                location=param.location
            )
            self.symbol_table.define(symbol)

            # Resolve default value if present
            if param.default_value:
                self.resolve_expression(param.default_value)

        except SemanticError as e:
            self.errors.append(e)

    # ========================================================================
    # Statement Resolution
    # ========================================================================

    def resolve_statement(self, stmt: ASTNode) -> None:
        """Resolve names in a statement.

        Args:
            stmt: Statement node
        """
        if isinstance(stmt, VarDeclStmt):
            self.resolve_var_decl(stmt)
        elif isinstance(stmt, AssignmentStmt):
            self.resolve_assignment(stmt)
        elif isinstance(stmt, ReturnStmt):
            self.resolve_return(stmt)
        elif isinstance(stmt, IfStmt):
            self.resolve_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self.resolve_while(stmt)
        elif isinstance(stmt, ForStmt):
            self.resolve_for(stmt)
        elif isinstance(stmt, BlockStmt):
            self.resolve_block(stmt)
        elif isinstance(stmt, ExpressionStmt):
            self.resolve_expression(stmt.expression)
        # else: unknown statement type, silently ignore

    def resolve_var_decl(self, stmt: VarDeclStmt) -> None:
        """Resolve variable declaration.

        Args:
            stmt: Variable declaration statement node
        """
        # First resolve initializer (if any)
        if stmt.initializer:
            self.resolve_expression(stmt.initializer)

        # Then define the variable
        try:
            # Check if this is a const declaration (future feature, for now all are variables)
            is_const = False  # TODO: Add is_const attribute to VarDeclStmt

            symbol = Symbol(
                name=stmt.name,
                symbol_type='constant' if is_const else 'variable',
                data_type=stmt.var_type,
                location=stmt.location,
                is_constant=is_const
            )
            self.symbol_table.define(symbol)
        except SemanticError as e:
            self.errors.append(e)

    def resolve_assignment(self, stmt: AssignmentStmt) -> None:
        """Resolve assignment (check target exists).

        Args:
            stmt: Assignment statement node
        """
        # Check if target variable is defined
        if isinstance(stmt.target, IdentifierExpr):
            symbol = self.symbol_table.lookup(stmt.target.name)
            if not symbol:
                self.errors.append(SemanticError(
                    f"Undefined variable: '{stmt.target.name}'",
                    stmt.location
                ))

        # Resolve value expression
        self.resolve_expression(stmt.value)

    def resolve_return(self, stmt: ReturnStmt) -> None:
        """Resolve return statement.

        Args:
            stmt: Return statement node
        """
        if stmt.value:
            self.resolve_expression(stmt.value)

    def resolve_if(self, stmt: IfStmt) -> None:
        """Resolve if statement.

        Args:
            stmt: If statement node
        """
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.then_branch)
        if stmt.else_branch:
            self.resolve_statement(stmt.else_branch)

    def resolve_while(self, stmt: WhileStmt) -> None:
        """Resolve while loop.

        Args:
            stmt: While statement node
        """
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.body)

    def resolve_for(self, stmt: ForStmt) -> None:
        """Resolve for loop.

        Args:
            stmt: For statement node
        """
        # For MVP, ForStmt has: variable (string), iterable (expr), body (stmt)
        # Define loop variable with int type (for range() iterables)
        # Note: We define it in the current scope (function scope), not a new scope
        # This matches Python/JavaScript behavior where loop variables are function-scoped
        # TODO: For full implementation, infer type from iterable
        int_type = PrimitiveType(location=stmt.location, name='int')
        loop_var_symbol = Symbol(
            name=stmt.variable,
            symbol_type='variable',
            data_type=int_type,
            location=stmt.location
        )
        try:
            self.symbol_table.define(loop_var_symbol)
        except SemanticError as e:
            self.errors.append(e)

        # Resolve iterable expression
        self.resolve_expression(stmt.iterable)

        # Resolve loop body
        self.resolve_statement(stmt.body)

    def resolve_block(self, stmt: BlockStmt) -> None:
        """Resolve block statement.

        Args:
            stmt: Block statement node
        """
        # Note: We don't create a new scope here because:
        # 1. Function bodies already have a scope (created by resolve_function)
        # 2. Control flow bodies (if/while/for) shouldn't create new scopes
        # 3. Variables declared in a function should be visible throughout the function
        #
        # If we need explicit block scoping in the future (e.g., for { } blocks),
        # we can add a flag to BlockStmt to indicate whether it should create a scope.

        for statement in stmt.statements:
            self.resolve_statement(statement)

    # ========================================================================
    # Expression Resolution
    # ========================================================================

    def resolve_expression(self, expr: ASTNode) -> None:
        """Resolve names in an expression.

        Args:
            expr: Expression node
        """
        if isinstance(expr, IdentifierExpr):
            self.resolve_identifier(expr)
        elif isinstance(expr, BinaryExpr):
            self.resolve_expression(expr.left)
            self.resolve_expression(expr.right)
        elif isinstance(expr, UnaryExpr):
            self.resolve_expression(expr.operand)
        elif isinstance(expr, CallExpr):
            self.resolve_call(expr)
        elif isinstance(expr, LambdaExpr):
            self.resolve_lambda(expr)
        elif isinstance(expr, LiteralExpr):
            pass  # Literals don't need resolution
        elif isinstance(expr, InterpolatedStringExpr):
            # Resolve interpolated expressions
            for interp_expr in expr.expressions:
                self.resolve_expression(interp_expr)
        # else: unknown expression type, silently ignore

    def resolve_identifier(self, expr: IdentifierExpr) -> None:
        """Check if identifier is defined.

        Args:
            expr: Identifier expression node
        """
        symbol = self.symbol_table.lookup(expr.name)
        if not symbol:
            self.errors.append(SemanticError(
                f"Undefined variable: '{expr.name}'",
                expr.location
            ))

    def resolve_call(self, expr: CallExpr) -> None:
        """Resolve function call.

        Args:
            expr: Call expression node
        """
        # Get function name from callee
        if isinstance(expr.callee, IdentifierExpr):
            func_name = expr.callee.name

            # Check if function is defined
            symbol = self.symbol_table.lookup(func_name)
            if not symbol:
                self.errors.append(SemanticError(
                    f"Undefined function: '{func_name}'",
                    expr.location
                ))
            elif symbol.symbol_type != 'function':
                self.errors.append(SemanticError(
                    f"'{func_name}' is not a function",
                    expr.location
                ))

        # Resolve arguments
        for arg in expr.arguments:
            self.resolve_expression(arg)

    def resolve_lambda(self, expr: LambdaExpr) -> None:
        """Resolve lambda expression.

        Args:
            expr: Lambda expression node
        """
        # Enter lambda scope
        self.symbol_table.enter_scope(f"lambda:{id(expr)}")

        try:
            # Register lambda parameters
            for param in expr.parameters:
                self.register_parameter(param)

            # Resolve lambda body
            # Lambda body can be a single expression or a BlockStmt
            if isinstance(expr.body, BlockStmt):
                for stmt in expr.body.statements:
                    self.resolve_statement(stmt)
            else:
                # Single expression body
                self.resolve_expression(expr.body)
        finally:
            try:
                self.symbol_table.exit_scope()
            except SemanticError:
                pass
