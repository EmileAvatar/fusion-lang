"""Name resolution for the Fusion semantic analyzer.

This module implements name resolution to link identifier uses to their declarations,
validate scoping rules, and detect undefined variables/functions.
"""

from typing import Optional, List
from src.parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    ExpressionStmt, BlockStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr, CallExpr, LambdaExpr, NamedArgument,
    InterpolatedStringExpr, StringExprPart, ArrayLiteralExpr, IndexExpr, MemberExpr,
    StructDecl, TypeNode, PrimitiveType, FunctionType, ArrayType, StructType
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

        # Scopes of the lambdas currently being resolved, innermost last - used to detect
        # closures (a lambda using a variable of the function around it, Task 18.1.3)
        self.lambda_scopes: List = []

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

        # len function: int len(array) - accepts any array type, so the parameter type
        # registered here is a placeholder; TypeChecker.visit_CallExpr special-cases 'len'
        # (like 'range' above) before the generic parameter-type check would ever see it
        len_type = FunctionType(
            parameter_types=[int_type],
            return_type=int_type,
            location=builtin_loc
        )

        len_symbol = Symbol(
            name='len',
            symbol_type='function',
            data_type=len_type,
            location=builtin_loc
        )

        try:
            self.symbol_table.define(len_symbol)
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

        # Pass 1: Register all struct and function declarations. Structs go first, so any
        # function signature can use any struct, wherever it's declared
        self.register_structs(program)
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
    # Pass 1: Struct Registration (Task 18.2.1)
    # ========================================================================

    def register_structs(self, program: ProgramNode) -> None:
        """Register every struct, then check their fields - in two loops, so a field (or
        any function signature) can name a struct declared later in the file."""
        structs = [d for d in program.declarations if isinstance(d, StructDecl)]
        for struct in structs:
            self.register_struct(struct)
        for struct in structs:
            self.check_struct(struct)

    def register_struct(self, struct: StructDecl) -> None:
        """Register a struct's name in the global scope.

        Sharing the global scope with functions and builtins means a struct can't have the
        same name as a function, another struct, or a builtin (`print`) - the duplicate is
        reported like any other.

        Args:
            struct: Struct declaration node
        """
        try:
            self.symbol_table.define(Symbol(
                name=struct.name,
                symbol_type='struct',
                data_type=StructType(location=struct.location, name=struct.name,
                                     declaration=struct),
                location=struct.location,
                declaration=struct
            ))
        except SemanticError as e:
            self.errors.append(e)

    def check_struct(self, struct: StructDecl) -> None:
        """Check a struct's fields.

        Field types: the primitives other than void, other structs (18.2.3 - how deep is
        checked separately, against the project's [structs] limits), and fixed-size arrays
        of either (18.2.3). Function-typed fields aren't planned (a struct holds plain values
        only).

        Args:
            struct: Struct declaration node
        """
        if not struct.fields:
            self.errors.append(SemanticError(
                f"Struct '{struct.name}' has no fields - a struct needs at least one",
                struct.location
            ))

        seen = set()
        for field in struct.fields:
            if field.name in seen:
                self.errors.append(SemanticError(
                    f"Struct '{struct.name}' has two fields named '{field.name}'",
                    field.location
                ))
            seen.add(field.name)

            field_type = field.field_type
            if isinstance(field_type, PrimitiveType) and field_type.name == 'void':
                self.errors.append(SemanticError(
                    f"Field '{field.name}' of struct '{struct.name}' can't be void",
                    field.location
                ))
            elif isinstance(field_type, FunctionType):
                self.errors.append(SemanticError(
                    f"Field '{field.name}' of struct '{struct.name}' can't hold a function - "
                    f"structs hold plain values only",
                    field.location
                ))
            elif isinstance(field_type, ArrayType):
                element = field_type.element_type
                if field_type.size is None:
                    self.errors.append(SemanticError(
                        f"Array field '{field.name}' of struct '{struct.name}' needs a size, "
                        f"e.g. {self._type_text(element)}[3] - a struct's size is fixed",
                        field.location
                    ))
                if isinstance(element, FunctionType) or (
                        isinstance(element, PrimitiveType) and element.name == 'void'):
                    self.errors.append(SemanticError(
                        f"Array field '{field.name}' of struct '{struct.name}' can't hold "
                        f"{'functions' if isinstance(element, FunctionType) else 'void'}",
                        field.location
                    ))
                self.resolve_type(field_type)
            elif isinstance(field_type, StructType):
                self.resolve_type(field_type)

            if field.default_value is not None and isinstance(field_type, (ArrayType, StructType)):
                self.errors.append(SemanticError(
                    f"Field '{field.name}' of struct '{struct.name}' can't have a default value - "
                    f"an array or struct field already starts with its own defaults (zero, or "
                    f"its fields' defaults)",
                    field.default_value.location
                ))
            elif field.default_value is not None and not self.is_constant_default(field.default_value):
                self.errors.append(SemanticError(
                    f"Default value for field '{field.name}' must be a constant (a "
                    f"literal such as 5, -1, 2.5, \"text\", 'c' or true)",
                    field.default_value.location
                ))

    def resolve_type(self, type_node: TypeNode) -> None:
        """Check that every struct named in a type exists, and link its declaration
        (Task 18.2.1). Recurses into array element types and function types.

        Args:
            type_node: The type to check
        """
        if isinstance(type_node, StructType):
            symbol = self.symbol_table.global_scope.lookup(type_node.name)
            if symbol is not None and symbol.symbol_type == 'struct':
                type_node.declaration = symbol.declaration
            else:
                self.errors.append(SemanticError(
                    f"Unknown type '{type_node.name}'",
                    type_node.location
                ))
        elif isinstance(type_node, ArrayType):
            self.resolve_type(type_node.element_type)
        elif isinstance(type_node, FunctionType):
            for param_type in type_node.parameter_types:
                self.resolve_type(param_type)
            self.resolve_type(type_node.return_type)

    @staticmethod
    def _type_text(type_node: TypeNode) -> str:
        """A short name for a type in messages."""
        return getattr(type_node, 'name', 'int')

    def check_not_struct_name(self, name: str, kind: str, location) -> None:
        """A variable or parameter can't reuse a struct's name - in the generated C it would
        hide the struct's type for the rest of its scope (Task 18.2.1)."""
        symbol = self.symbol_table.global_scope.lookup(name)
        if symbol is not None and symbol.symbol_type == 'struct':
            self.errors.append(SemanticError(
                f"{kind} '{name}' has the same name as struct '{name}' - choose another name",
                location
            ))

    # ========================================================================
    # Pass 1: Function Registration
    # ========================================================================

    def register_function(self, func: FunctionDecl) -> None:
        """Register a function in the global symbol table.

        Args:
            func: Function declaration node
        """
        # Array parameters are supported (Task 18.1.2); array return values are not - C
        # can't return an array, and wrapping one in a struct needs structs (Task 18.2)
        if isinstance(func.return_type, ArrayType):
            self.errors.append(SemanticError(
                "Arrays are not yet supported as function return types",
                func.location
            ))

        self.check_parameter_defaults(func)

        # Struct names in the signature (Task 18.2.1)
        self.resolve_type(func.return_type)
        for param in func.parameters:
            self.resolve_type(param.param_type)

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
                location=func.location,
                declaration=func
            )

            # Add to global scope
            self.symbol_table.define(symbol)

        except SemanticError as e:
            self.errors.append(e)

    def check_parameter_defaults(self, func: FunctionDecl) -> None:
        """Check the rules for parameter default values (Task 18.1.1).

        - Once a parameter has a default, every parameter after it must have one too -
          otherwise a call that omits arguments can't tell which ones were left out.
        - A default must be a compile-time constant: a literal, or a negated number literal.
          C has no default arguments, so codegen copies the default into every call site
          that omits it; a constant reads the same everywhere, while an expression naming a
          parameter or variable would refer to something that doesn't exist at the caller.

        Args:
            func: Function declaration node
        """
        seen_default = None
        for param in func.parameters:
            if param.default_value is None:
                if seen_default is not None:
                    self.errors.append(SemanticError(
                        f"Parameter '{param.name}' needs a default value, because it comes "
                        f"after parameter '{seen_default}', which has one - parameters with "
                        f"defaults must come last",
                        param.location
                    ))
                continue

            seen_default = param.name
            if isinstance(param.param_type, ArrayType):
                self.errors.append(SemanticError(
                    f"Array parameter '{param.name}' can't have a default value",
                    param.location
                ))
            elif not self.is_constant_default(param.default_value):
                self.errors.append(SemanticError(
                    f"Default value for parameter '{param.name}' must be a constant (a "
                    f"literal such as 5, -1, 2.5, \"text\", 'c' or true)",
                    param.default_value.location
                ))

    @staticmethod
    def is_constant_default(expr) -> bool:
        """Return True if expr is allowed as a parameter default: a literal (other than
        null), or a negated int/float literal such as -1."""
        if isinstance(expr, LiteralExpr):
            return expr.type_hint != 'null'
        if isinstance(expr, UnaryExpr) and expr.operator == '-':
            operand = expr.operand
            return isinstance(operand, LiteralExpr) and operand.type_hint in ('int', 'float', 'double')
        return False

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

            # Resolve function body. If it's a block (the normal case - lambdas can have a
            # single expression body instead), it shares the parameter scope directly
            # rather than nesting a new one - see resolve_block's new_scope docstring.
            if func.body:
                if isinstance(func.body, BlockStmt):
                    self.resolve_block(func.body, new_scope=False)
                else:
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
        self.check_not_struct_name(param.name, "Parameter", param.location)
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
        # Check if const has initializer
        if stmt.is_const and not stmt.initializer:
            self.errors.append(SemanticError(
                f"const declaration '{stmt.name}' must have an initializer",
                stmt.location
            ))

        self.resolve_type(stmt.var_type)
        self.check_not_struct_name(stmt.name, "Variable", stmt.location)

        # First resolve initializer (if any)
        if stmt.initializer:
            self.resolve_expression(stmt.initializer)

        # Then define the variable
        try:
            # Check if this is a const declaration
            is_const = stmt.is_const

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
        elif isinstance(stmt.target, (MemberExpr, IndexExpr)):
            self.resolve_expression(stmt.target)

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
        # Block scoping (Task 12.6): the loop variable gets its own scope, one level above
        # the body's own block scope - matches C's `for (int i = ...; ...) { ... }`, where
        # `i` is visible inside the loop (including the body block) but not after it.
        # Stored on stmt.scope so TypeChecker's separate pass can reuse the same, already-
        # populated scope object instead of re-declaring the loop variable itself.
        self.symbol_table.enter_scope(f"for:{id(stmt)}")
        stmt.scope = self.symbol_table.current_scope

        try:
            # Define loop variable with int type (for range() iterables)
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

            # Resolve loop body (a BlockStmt - creates its own nested scope, parented to
            # this for-scope, so the body can see the loop variable via lookup_recursive)
            self.resolve_statement(stmt.body)
        finally:
            self.symbol_table.exit_scope()

    def resolve_block(self, stmt: BlockStmt, new_scope: bool = True) -> None:
        """Resolve block statement.

        Block scoping (Task 12.6): each block gets its own scope, so a variable declared
        inside an if/while/for body is only visible inside that block - matching what the
        generated C code already does (C's own { } braces are block-scoped natively; this
        was previously a real bug, not just a style choice - Fusion's semantic analyzer
        allowed cross-block visibility that the C output could never actually honor, so
        such programs passed semantic analysis but failed to compile with GCC).

        The scope is stored on stmt.scope so TypeChecker's separate pass over the same
        tree can reuse these exact, already-populated scopes (enter_existing_scope)
        instead of re-declaring every variable a second time.

        Args:
            stmt: Block statement node
            new_scope: Whether this block introduces its own nested scope (the default,
                correct for if/while/for bodies and any other nested block). Pass False
                only for a function's own top-level body, which must share the parameter
                scope directly rather than nest below it - confirmed against real GCC:
                redeclaring a parameter at the top level of a function body is itself a C
                compile error ('redeclared as different kind of symbol'), so nesting
                another scope there would silently let Fusion accept programs that fail
                to compile, again - see resolve_function and semantic_analyzer.py.
        """
        if not new_scope:
            # Share the current (function+parameter) scope - no new nesting
            stmt.scope = self.symbol_table.current_scope
            for statement in stmt.statements:
                self.resolve_statement(statement)
            return

        self.symbol_table.enter_scope(f"block:{id(stmt)}")
        stmt.scope = self.symbol_table.current_scope

        try:
            for statement in stmt.statements:
                self.resolve_statement(statement)
        finally:
            self.symbol_table.exit_scope()

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
            # Resolve interpolated expressions (skip literal text segments)
            for segment in expr.segments:
                if isinstance(segment, StringExprPart):
                    self.resolve_expression(segment.expression)
        elif isinstance(expr, ArrayLiteralExpr):
            for element in expr.elements:
                self.resolve_expression(element)
        elif isinstance(expr, IndexExpr):
            self.resolve_expression(expr.array)
            self.resolve_expression(expr.index)
        elif isinstance(expr, NamedArgument):
            self.resolve_expression(expr.value)
        elif isinstance(expr, MemberExpr):
            # Only the object needs resolving - the field name is checked by the type
            # checker, once the object's struct type is known
            self.resolve_expression(expr.object)
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
        elif self.lambda_scopes and self.is_captured(expr.name):
            self.errors.append(SemanticError(
                f"Lambda uses '{expr.name}' from the surrounding function - closures "
                f"(capturing variables) are not supported yet. Pass '{expr.name}' to the "
                f"lambda as a parameter instead",
                expr.location
            ))

    def is_captured(self, name: str) -> bool:
        """Return True if `name`, used inside the innermost lambda, is defined outside that
        lambda but not at global scope - i.e. using it would make the lambda a closure.

        A closure must keep the captured variable alive after the function that created
        the lambda returns, which needs heap memory and an ownership rule (Task 18.3), so
        v1 lambdas can only use their own parameters and global names (functions).
        """
        lambda_scope = self.lambda_scopes[-1]
        scope = self.symbol_table.current_scope
        while scope is not None:
            if name in scope.symbols:
                return False  # defined inside the lambda (its parameters or deeper)
            if scope is lambda_scope:
                break
            scope = scope.parent
        # Defined outside the lambda - fine only if it's a global (e.g. a function)
        return name not in self.symbol_table.global_scope.symbols

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
            elif symbol.symbol_type == 'struct':
                pass  # A struct constructor, Point(3, 4) (Task 18.2.1)
            elif symbol.symbol_type != 'function' and not isinstance(symbol.data_type, FunctionType):
                # A variable or parameter holding a function can be called (Task 18.1.3)
                self.errors.append(SemanticError(
                    f"'{func_name}' is not a function",
                    expr.location
                ))
            elif self.lambda_scopes and symbol.symbol_type != 'function' and self.is_captured(func_name):
                self.errors.append(SemanticError(
                    f"Lambda uses '{func_name}' from the surrounding function - closures "
                    f"(capturing variables) are not supported yet",
                    expr.location
                ))
        else:
            # Calling the result of an expression, e.g. (func(int x) : x * 2)(5)
            self.resolve_expression(expr.callee)

        # Resolve arguments
        for arg in expr.arguments:
            self.resolve_expression(arg)

    def resolve_lambda(self, expr: LambdaExpr) -> None:
        """Resolve lambda expression.

        Args:
            expr: Lambda expression node
        """
        # Enter lambda scope - stored on the node so the type checker re-enters the same,
        # already-populated scope (Task 18.1.3)
        self.symbol_table.enter_scope(f"lambda:{id(expr)}")
        expr.scope = self.symbol_table.current_scope
        self.lambda_scopes.append(expr.scope)

        try:
            # Register lambda parameters. A lambda is called through a function value, which
            # carries only parameter types - so its parameters can't have defaults
            for param in expr.parameters:
                self.resolve_type(param.param_type)
                if param.default_value is not None:
                    self.errors.append(SemanticError(
                        f"Lambda parameter '{param.name}' can't have a default value",
                        param.location
                    ))
                self.register_parameter(param)

            # Resolve lambda body - a single expression, or a BlockStmt sharing the
            # parameter scope (via resolve_block, so its .scope is set - fixes Task 15.3)
            if isinstance(expr.body, BlockStmt):
                self.resolve_block(expr.body, new_scope=False)
            else:
                # Single expression body
                self.resolve_expression(expr.body)
        finally:
            self.lambda_scopes.pop()
            try:
                self.symbol_table.exit_scope()
            except SemanticError:
                pass
