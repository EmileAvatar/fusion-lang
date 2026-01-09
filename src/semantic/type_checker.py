"""Type checking for the Fusion semantic analyzer.

This module implements type checking to validate type compatibility in expressions,
assignments, function calls, and return statements.
"""

from typing import Optional, List
from src.parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    BreakStmt, ContinueStmt, ExpressionStmt, BlockStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr, CallExpr, LambdaExpr,
    InterpolatedStringExpr,
    TypeNode, PrimitiveType, FunctionType
)
from .symbol_table import SymbolTable
from .symbol import Symbol
from .errors import SemanticError
from src.lexer.token import SourceLocation


class TypeChecker:
    """Type checks the AST using visitor pattern.

    Validates type compatibility in expressions, assignments, function calls,
    and return statements. Collects all type errors and returns them for reporting.

    Attributes:
        symbol_table: Symbol table for looking up variable/function types
        current_function_return_type: Expected return type of current function
        errors: List of semantic errors found during type checking
    """

    def __init__(self, symbol_table: SymbolTable):
        """Initialize type checker.

        Args:
            symbol_table: Symbol table for symbol lookup
        """
        self.symbol_table = symbol_table
        self.current_function_return_type: Optional[TypeNode] = None
        self.errors: List[SemanticError] = []

    def check_program(self, program: ProgramNode) -> List[SemanticError]:
        """Type check entire program.

        Args:
            program: Root AST node

        Returns:
            List of semantic errors found (empty if no errors)
        """
        self.errors = []  # Reset errors
        for decl in program.declarations:
            self.visit(decl)
        return self.errors

    def visit(self, node: ASTNode) -> Optional[TypeNode]:
        """Dispatch to appropriate visit method based on node type.

        Args:
            node: AST node to visit

        Returns:
            Type of the expression, or None for statements

        Raises:
            NotImplementedError: If no visitor method exists for node type
        """
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode):
        """Fallback for unhandled node types.

        Args:
            node: Unhandled AST node

        Raises:
            NotImplementedError: Always raised for unhandled nodes
        """
        raise NotImplementedError(f"No visitor for {node.__class__.__name__}")

    # ========================================================================
    # Type Compatibility and Helper Methods
    # ========================================================================

    def types_compatible(self, expected: TypeNode, actual: TypeNode) -> bool:
        """Check if two types are compatible (assignment/parameter passing).

        Args:
            expected: Expected target type
            actual: Actual source type

        Returns:
            True if actual can be used where expected is required
        """
        # Exact match
        if self.types_equal(expected, actual):
            return True

        # Numeric promotions (int -> float -> double)
        if self.is_numeric_promotion(expected, actual):
            return True

        return False

    def types_equal(self, type1: TypeNode, type2: TypeNode) -> bool:
        """Check if two types are exactly equal.

        Args:
            type1: First type
            type2: Second type

        Returns:
            True if types are identical
        """
        if isinstance(type1, PrimitiveType) and isinstance(type2, PrimitiveType):
            return type1.name == type2.name

        if isinstance(type1, FunctionType) and isinstance(type2, FunctionType):
            # Check return types match
            if not self.types_equal(type1.return_type, type2.return_type):
                return False
            # Check parameter counts match
            if len(type1.parameter_types) != len(type2.parameter_types):
                return False
            # Check each parameter type matches
            for p1, p2 in zip(type1.parameter_types, type2.parameter_types):
                if not self.types_equal(p1, p2):
                    return False
            return True

        return False

    def is_numeric_promotion(self, target: TypeNode, source: TypeNode) -> bool:
        """Check if source can be promoted to target (int->float->double).

        Args:
            target: Target type
            source: Source type

        Returns:
            True if promotion is valid
        """
        if not isinstance(target, PrimitiveType) or not isinstance(source, PrimitiveType):
            return False

        # Promotion hierarchy: int -> float -> double
        promotions = {
            'double': ['int', 'float', 'double'],
            'float': ['int', 'float'],
            'int': ['int']
        }

        return source.name in promotions.get(target.name, [])

    def get_wider_type(self, type1: TypeNode, type2: TypeNode) -> TypeNode:
        """Get the wider of two numeric types (for arithmetic result type).

        Args:
            type1: First type
            type2: Second type

        Returns:
            Wider type (double > float > int)
        """
        if not isinstance(type1, PrimitiveType) or not isinstance(type2, PrimitiveType):
            return PrimitiveType('void', location=type1.location)

        # Width hierarchy: double > float > int
        widths = {'double': 3, 'float': 2, 'int': 1}
        width1 = widths.get(type1.name, 0)
        width2 = widths.get(type2.name, 0)

        if width1 >= width2:
            return type1
        return type2

    def is_numeric_type(self, type_node: TypeNode) -> bool:
        """Check if type is numeric (int, float, double).

        Args:
            type_node: Type to check

        Returns:
            True if numeric type
        """
        if not isinstance(type_node, PrimitiveType):
            return False
        return type_node.name in ['int', 'float', 'double']

    def is_bool_type(self, type_node: TypeNode) -> bool:
        """Check if type is bool.

        Args:
            type_node: Type to check

        Returns:
            True if bool type
        """
        return isinstance(type_node, PrimitiveType) and type_node.name == 'bool'

    def type_to_string(self, type_node: TypeNode) -> str:
        """Convert type node to string for error messages.

        Args:
            type_node: Type node

        Returns:
            String representation of type
        """
        if isinstance(type_node, PrimitiveType):
            return type_node.name
        if isinstance(type_node, FunctionType):
            params = ", ".join(self.type_to_string(p) for p in type_node.parameter_types)
            ret = self.type_to_string(type_node.return_type)
            return f"({params}) -> {ret}"
        return "unknown"

    # ========================================================================
    # Expression Visitors
    # ========================================================================

    def visit_LiteralExpr(self, node: LiteralExpr) -> TypeNode:
        """Return the type of a literal.

        Args:
            node: Literal expression node

        Returns:
            Type of the literal
        """
        # Map literal type hints to actual types
        type_map = {
            'int': 'int',
            'float': 'float',
            'double': 'double',
            'string': 'string',
            'char': 'char',
            'bool': 'bool',
            'null': 'void'  # null is treated as void type
        }
        type_name = type_map.get(node.type_hint, 'void')
        return PrimitiveType(location=node.location, name=type_name)

    def visit_IdentifierExpr(self, node: IdentifierExpr) -> TypeNode:
        """Look up identifier type in symbol table.

        Args:
            node: Identifier expression node

        Returns:
            Type of the identifier (void if undefined for error recovery)
        """
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.errors.append(SemanticError(
                f"Undefined variable: '{node.name}'",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')
        return symbol.data_type

    def visit_BinaryExpr(self, node: BinaryExpr) -> TypeNode:
        """Check binary operation type compatibility.

        Args:
            node: Binary expression node

        Returns:
            Result type of the binary operation
        """
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Arithmetic operators: int/float/double + int/float/double
        if node.operator in ['+', '-', '*', '/', '%']:
            if not self.is_numeric_type(left_type):
                self.errors.append(SemanticError(
                    f"Left operand of '{node.operator}' must be numeric, got {self.type_to_string(left_type)}",
                    node.left.location
                ))
            if not self.is_numeric_type(right_type):
                self.errors.append(SemanticError(
                    f"Right operand of '{node.operator}' must be numeric, got {self.type_to_string(right_type)}",
                    node.right.location
                ))
            # Result type is the wider of the two
            return self.get_wider_type(left_type, right_type)

        # Comparison operators: comparable types -> bool
        if node.operator in ['<', '>', '<=', '>=', '==', '!=']:
            # For equality, any types can be compared (just checking if they're compatible)
            if node.operator in ['==', '!=']:
                # Allow comparison of any types
                pass
            else:
                # For ordering comparisons, require numeric types
                if not self.is_numeric_type(left_type):
                    self.errors.append(SemanticError(
                        f"Left operand of '{node.operator}' must be numeric, got {self.type_to_string(left_type)}",
                        node.left.location
                    ))
                if not self.is_numeric_type(right_type):
                    self.errors.append(SemanticError(
                        f"Right operand of '{node.operator}' must be numeric, got {self.type_to_string(right_type)}",
                        node.right.location
                    ))
            return PrimitiveType(location=node.location, name='bool')

        # Logical operators: bool and bool -> bool
        if node.operator in ['and', 'or', '&&', '||']:
            if not self.is_bool_type(left_type):
                self.errors.append(SemanticError(
                    f"Left operand of '{node.operator}' must be bool, got {self.type_to_string(left_type)}",
                    node.left.location
                ))
            if not self.is_bool_type(right_type):
                self.errors.append(SemanticError(
                    f"Right operand of '{node.operator}' must be bool, got {self.type_to_string(right_type)}",
                    node.right.location
                ))
            return PrimitiveType(location=node.location, name='bool')

        # Unknown operator - return void for error recovery
        return PrimitiveType('void', location=node.location)

    def visit_UnaryExpr(self, node: UnaryExpr) -> TypeNode:
        """Check unary operation type.

        Args:
            node: Unary expression node

        Returns:
            Result type of the unary operation
        """
        operand_type = self.visit(node.operand)

        if node.operator == '-':
            if not self.is_numeric_type(operand_type):
                self.errors.append(SemanticError(
                    f"Unary minus requires numeric type, got {self.type_to_string(operand_type)}",
                    node.operand.location
                ))
            return operand_type

        if node.operator in ['not', '!']:
            if not self.is_bool_type(operand_type):
                self.errors.append(SemanticError(
                    f"Logical not requires bool type, got {self.type_to_string(operand_type)}",
                    node.operand.location
                ))
            return PrimitiveType(location=node.location, name='bool')

        # Unknown operator - return void for error recovery
        return PrimitiveType('void', location=node.location)

    def visit_CallExpr(self, node: CallExpr) -> TypeNode:
        """Check function call argument types.

        Args:
            node: Call expression node

        Returns:
            Return type of the function
        """
        # Get function name (callee should be IdentifierExpr)
        if not isinstance(node.callee, IdentifierExpr):
            self.errors.append(SemanticError(
                "Function call callee must be an identifier",
                node.callee.location
            ))
            return PrimitiveType(location=node.location, name='void')

        func_name = node.callee.name

        # Look up function
        symbol = self.symbol_table.lookup(func_name)
        if not symbol:
            self.errors.append(SemanticError(
                f"Undefined function: '{func_name}'",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        if symbol.symbol_type != 'function':
            self.errors.append(SemanticError(
                f"'{func_name}' is not a function",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        # Get function type
        func_type = symbol.data_type
        if not isinstance(func_type, FunctionType):
            return PrimitiveType(location=node.location, name='void')

        # Check argument count
        # Special case for range() function: accepts 2 or 3 arguments
        if func_name == 'range':
            actual_count = len(node.arguments)
            if actual_count < 2 or actual_count > 3:
                self.errors.append(SemanticError(
                    f"Function 'range' expects 2 or 3 argument(s), got {actual_count}",
                    node.location
                ))
                return func_type.return_type
            # For range(), only check the arguments that were provided
            for i, arg in enumerate(node.arguments):
                if i < len(func_type.parameter_types):
                    actual_type = self.visit(arg)
                    expected_type = func_type.parameter_types[i]
                    if not self.types_compatible(expected_type, actual_type):
                        self.errors.append(SemanticError(
                            f"Argument {i+1} to 'range': expected {self.type_to_string(expected_type)}, "
                            f"got {self.type_to_string(actual_type)}",
                            arg.location
                        ))
            return func_type.return_type

        expected_count = len(func_type.parameter_types)
        actual_count = len(node.arguments)
        if actual_count != expected_count:
            self.errors.append(SemanticError(
                f"Function '{func_name}' expects {expected_count} argument(s), got {actual_count}",
                node.location
            ))
            return func_type.return_type

        # Check each argument type
        for i, (arg, expected_type) in enumerate(zip(node.arguments, func_type.parameter_types)):
            actual_type = self.visit(arg)
            if not self.types_compatible(expected_type, actual_type):
                self.errors.append(SemanticError(
                    f"Argument {i+1} to '{func_name}': expected {self.type_to_string(expected_type)}, "
                    f"got {self.type_to_string(actual_type)}",
                    arg.location
                ))

        return func_type.return_type

    def visit_LambdaExpr(self, node: LambdaExpr) -> TypeNode:
        """Check lambda expression.

        Args:
            node: Lambda expression node

        Returns:
            Function type of the lambda
        """
        # Get parameter types
        param_types = [param.param_type for param in node.parameters]

        # Create function type
        func_type = FunctionType(
            parameter_types=param_types,
            return_type=node.return_type,
            location=node.location
        )

        # Check body (enter function scope for return type checking)
        old_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type

        # Visit body
        self.visit(node.body)

        self.current_function_return_type = old_return_type

        return func_type

    def visit_InterpolatedStringExpr(self, node: InterpolatedStringExpr) -> TypeNode:
        """Check interpolated string expression.

        Args:
            node: Interpolated string expression node

        Returns:
            String type
        """
        # Check each interpolated expression
        for expr in node.expressions:
            self.visit(expr)  # Just type check, don't validate type

        return PrimitiveType(location=node.location, name='string')

    # ========================================================================
    # Statement Visitors
    # ========================================================================

    def visit_ExpressionStmt(self, node: ExpressionStmt) -> None:
        """Check expression statement.

        Args:
            node: Expression statement node
        """
        self.visit(node.expression)

    def visit_VarDeclStmt(self, node: VarDeclStmt) -> None:
        """Check variable declaration type matches initializer.

        Args:
            node: Variable declaration statement node
        """
        if node.initializer:
            init_type = self.visit(node.initializer)
            if not self.types_compatible(node.var_type, init_type):
                self.errors.append(SemanticError(
                    f"Cannot assign {self.type_to_string(init_type)} to variable of type {self.type_to_string(node.var_type)}",
                    node.location
                ))

    def visit_AssignmentStmt(self, node: AssignmentStmt) -> None:
        """Check assignment type compatibility.

        Args:
            node: Assignment statement node
        """
        # Target should be IdentifierExpr
        if not isinstance(node.target, IdentifierExpr):
            self.errors.append(SemanticError(
                "Assignment target must be an identifier",
                node.target.location
            ))
            return

        target_name = node.target.name

        # Look up target variable
        symbol = self.symbol_table.lookup(target_name)
        if not symbol:
            self.errors.append(SemanticError(
                f"Undefined variable: '{target_name}'",
                node.location
            ))
            return

        # Check if constant
        if symbol.is_constant:
            self.errors.append(SemanticError(
                f"Cannot assign to constant: '{target_name}'",
                node.location
            ))

        # Check type compatibility
        value_type = self.visit(node.value)
        if not self.types_compatible(symbol.data_type, value_type):
            self.errors.append(SemanticError(
                f"Cannot assign {self.type_to_string(value_type)} to variable of type {self.type_to_string(symbol.data_type)}",
                node.location
            ))

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        """Check return type matches function return type.

        Args:
            node: Return statement node
        """
        if not self.current_function_return_type:
            self.errors.append(SemanticError(
                "Return statement outside function",
                node.location
            ))
            return

        if node.value:
            return_type = self.visit(node.value)
            if not self.types_compatible(self.current_function_return_type, return_type):
                self.errors.append(SemanticError(
                    f"Return type {self.type_to_string(return_type)} does not match function return type {self.type_to_string(self.current_function_return_type)}",
                    node.location
                ))
        else:
            # No return value (empty return statement)
            if not isinstance(self.current_function_return_type, PrimitiveType) or \
               self.current_function_return_type.name != 'void':
                self.errors.append(SemanticError(
                    f"Function must return {self.type_to_string(self.current_function_return_type)}",
                    node.location
                ))

    def visit_IfStmt(self, node: IfStmt) -> None:
        """Check if statement condition is bool.

        Args:
            node: If statement node
        """
        condition_type = self.visit(node.condition)
        if not self.is_bool_type(condition_type):
            self.errors.append(SemanticError(
                f"If condition must be bool, got {self.type_to_string(condition_type)}",
                node.condition.location
            ))

        # Check branches
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileStmt(self, node: WhileStmt) -> None:
        """Check while loop condition is bool.

        Args:
            node: While statement node
        """
        condition_type = self.visit(node.condition)
        if not self.is_bool_type(condition_type):
            self.errors.append(SemanticError(
                f"While condition must be bool, got {self.type_to_string(condition_type)}",
                node.condition.location
            ))

        # Check body
        self.visit(node.body)

    def visit_ForStmt(self, node: ForStmt) -> None:
        """Check for loop (basic check for now).

        Args:
            node: For statement node
        """
        # Type check iterable expression
        self.visit(node.iterable)

        # Note: Loop variable was already defined by name_resolver in function scope
        # No need to create a new scope here

        # Check body
        self.visit(node.body)

    def visit_BlockStmt(self, node: BlockStmt) -> None:
        """Check all statements in block.

        Args:
            node: Block statement node
        """
        for stmt in node.statements:
            self.visit(stmt)

    def visit_BreakStmt(self, node: BreakStmt) -> None:
        """Check break statement.

        Args:
            node: Break statement node
        """
        # Break statements are validated by ControlFlowValidator
        # No type checking needed here
        pass

    def visit_ContinueStmt(self, node: ContinueStmt) -> None:
        """Check continue statement.

        Args:
            node: Continue statement node
        """
        # Continue statements are validated by ControlFlowValidator
        # No type checking needed here
        pass

    # ========================================================================
    # Declaration Visitors
    # ========================================================================

    def visit_FunctionDecl(self, node: FunctionDecl) -> None:
        """Check function declaration.

        NOTE: This visitor is not used when called from SemanticAnalyzer,
        which manually manages scopes. This is only used for standalone
        type checking in tests.

        Args:
            node: Function declaration node
        """
        # Set current function return type
        old_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type

        # Enter function scope (parameters are registered here by NameResolver)
        self.symbol_table.enter_scope(f"function:{node.name}")

        try:
            # Check parameters
            for param in node.parameters:
                self.visit(param)

            # Check body
            self.visit(node.body)
        finally:
            # Always exit scope
            try:
                self.symbol_table.exit_scope()
            except:
                pass  # Scope already exited

        self.current_function_return_type = old_return_type

    def visit_ParameterDecl(self, node: ParameterDecl) -> None:
        """Check parameter declaration.

        Args:
            node: Parameter declaration node
        """
        # Check default value type if present
        if node.default_value:
            default_type = self.visit(node.default_value)
            if not self.types_compatible(node.param_type, default_type):
                self.errors.append(SemanticError(
                    f"Default value type {self.type_to_string(default_type)} does not match parameter type {self.type_to_string(node.param_type)}",
                    node.location
                ))

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Check program (handled by check_program).

        Args:
            node: Program node
        """
        for decl in node.declarations:
            self.visit(decl)
