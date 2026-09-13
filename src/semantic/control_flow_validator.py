"""
Control Flow Validator for Fusion Programming Language

This module validates control flow semantics:
- Non-void functions must return on all code paths
- Unreachable code detection (warnings)
- Break/continue only allowed inside loops
- Loop/if conditions must be boolean type
"""

from typing import List, Optional, Tuple
from src.parser.ast_nodes import *
from src.semantic.type_checker import TypeChecker


class SemanticError(Exception):
    """Semantic analysis error with source location."""

    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location
        super().__init__(f"{message} at {location}")


class ControlFlowValidator:
    """Validates control flow semantics in Fusion programs."""

    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []
        self.in_loop: int = 0  # Loop nesting depth
        self.current_function_return_type: Optional[TypeNode] = None

    def validate_program(self, program: ProgramNode, type_checker: TypeChecker) -> Tuple[List[SemanticError], List[SemanticError]]:
        """Validate control flow in entire program.

        Args:
            program: The program AST root node
            type_checker: Type checker instance for condition validation

        Returns:
            Tuple of (errors, warnings)
        """
        self.errors = []
        self.warnings = []

        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.validate_function(decl, type_checker)

        return self.errors, self.warnings

    def validate_function(self, func: FunctionDecl, type_checker: TypeChecker) -> None:
        """Validate control flow in a function.

        Args:
            func: Function declaration node
            type_checker: Type checker instance
        """
        self.current_function_return_type = func.return_type

        if func.body:
            # Check return paths
            returns = self.check_returns(func.body)

            # Non-void functions must return on all paths
            if self.get_type_name(func.return_type) != 'void' and not returns:
                self.errors.append(SemanticError(
                    f"Function '{func.name}' must return {self.format_type(func.return_type)} on all code paths",
                    func.location
                ))

            # Check for unreachable code
            self.check_unreachable_code(func.body)

            # Validate break/continue usage
            self.validate_statement(func.body)

            # Validate condition types
            self.validate_conditions(func.body, type_checker)

        self.current_function_return_type = None

    # ========================================================================
    # Return Path Analysis
    # ========================================================================

    def check_returns(self, stmt: ASTNode) -> bool:
        """Check if a statement always returns.

        Args:
            stmt: Statement node to check

        Returns:
            True if all code paths return, False otherwise
        """
        if isinstance(stmt, ReturnStmt):
            return True

        elif isinstance(stmt, BlockStmt):
            # Block returns if any statement returns
            for s in stmt.statements:
                if self.check_returns(s):
                    return True
            return False

        elif isinstance(stmt, IfStmt):
            # If returns only if both branches return
            if stmt.else_branch:
                then_returns = self.check_returns(stmt.then_branch)
                else_returns = self.check_returns(stmt.else_branch)
                return then_returns and else_returns
            return False

        elif isinstance(stmt, WhileStmt):
            # While loops don't guarantee return (might not execute)
            return False

        elif isinstance(stmt, ForStmt):
            # For loops don't guarantee return (might not execute)
            return False

        else:
            return False

    # ========================================================================
    # Unreachable Code Detection
    # ========================================================================

    def check_unreachable_code(self, stmt: ASTNode) -> None:
        """Detect unreachable code after return/break/continue.

        Args:
            stmt: Statement node to check
        """
        if isinstance(stmt, BlockStmt):
            found_terminal = False
            for i, s in enumerate(stmt.statements):
                if found_terminal:
                    # Code after return/break/continue
                    self.warnings.append(SemanticError(
                        "Unreachable code detected",
                        s.location
                    ))
                    break  # Only warn once per block

                if self.is_terminal_statement(s):
                    found_terminal = True

                # Recursively check nested statements
                self.check_unreachable_code(s)

        elif isinstance(stmt, IfStmt):
            self.check_unreachable_code(stmt.then_branch)
            if stmt.else_branch:
                self.check_unreachable_code(stmt.else_branch)

        elif isinstance(stmt, WhileStmt):
            self.check_unreachable_code(stmt.body)

        elif isinstance(stmt, ForStmt):
            self.check_unreachable_code(stmt.body)

    def is_terminal_statement(self, stmt: ASTNode) -> bool:
        """Check if statement terminates execution (return/break/continue).

        Args:
            stmt: Statement node to check

        Returns:
            True if statement terminates execution
        """
        return isinstance(stmt, (ReturnStmt, BreakStmt, ContinueStmt))

    # ========================================================================
    # Break/Continue Validation
    # ========================================================================

    def validate_statement(self, stmt: ASTNode) -> None:
        """Validate break/continue usage in a statement.

        Args:
            stmt: Statement node to validate
        """
        if isinstance(stmt, BreakStmt):
            if self.in_loop == 0:
                self.errors.append(SemanticError(
                    "Break statement outside loop",
                    stmt.location
                ))

        elif isinstance(stmt, ContinueStmt):
            if self.in_loop == 0:
                self.errors.append(SemanticError(
                    "Continue statement outside loop",
                    stmt.location
                ))

        elif isinstance(stmt, WhileStmt):
            self.in_loop += 1
            self.validate_statement(stmt.body)
            self.in_loop -= 1

        elif isinstance(stmt, ForStmt):
            self.in_loop += 1
            self.validate_statement(stmt.body)
            self.in_loop -= 1

        elif isinstance(stmt, BlockStmt):
            for s in stmt.statements:
                self.validate_statement(s)

        elif isinstance(stmt, IfStmt):
            self.validate_statement(stmt.then_branch)
            if stmt.else_branch:
                self.validate_statement(stmt.else_branch)

    # ========================================================================
    # Condition Type Validation
    # ========================================================================

    def validate_conditions(self, stmt: ASTNode, type_checker: TypeChecker) -> None:
        """Ensure all conditions are boolean type.

        Runs after the main type-checking walk has already finished and unwound its
        scopes (see semantic_analyzer.py: validate_function is called after
        type_checker.visit(decl.body) completes), so re-visiting a condition here can't
        rely on the type checker's scope stack already being positioned correctly - it
        has to re-enter the right scope itself. Block scoping (Task 12.6) means a
        condition inside a loop or nested block may reference names (like a for loop's
        own variable) that only exist in that block's scope, not the function's - see
        stmt.scope, populated by NameResolver and reused the same way
        TypeChecker.visit_BlockStmt does. Falls back to no scope change when stmt.scope
        is unset (this method is also used to validate a program that never had
        NameResolver run over it - see the ControlFlowValidator unit tests), matching
        this method's prior behavior exactly.

        Args:
            stmt: Statement node to validate
            type_checker: Type checker instance
        """
        if isinstance(stmt, IfStmt):
            cond_type = type_checker.visit(stmt.condition)
            if not self.is_bool_type(cond_type):
                self.errors.append(SemanticError(
                    f"If condition must be bool, got {self.format_type(cond_type)}",
                    stmt.condition.location
                ))
            self.validate_conditions(stmt.then_branch, type_checker)
            if stmt.else_branch:
                self.validate_conditions(stmt.else_branch, type_checker)

        elif isinstance(stmt, WhileStmt):
            cond_type = type_checker.visit(stmt.condition)
            if not self.is_bool_type(cond_type):
                self.errors.append(SemanticError(
                    f"While condition must be bool, got {self.format_type(cond_type)}",
                    stmt.condition.location
                ))
            self.validate_conditions(stmt.body, type_checker)

        elif isinstance(stmt, ForStmt):
            # For loops don't have explicit conditions in MVP (just iterable), but the
            # loop variable's scope (stmt.scope) needs to be active for conditions nested
            # inside the body to resolve it.
            if stmt.scope is not None:
                type_checker.symbol_table.enter_existing_scope(stmt.scope)
                try:
                    self.validate_conditions(stmt.body, type_checker)
                finally:
                    type_checker.symbol_table.exit_scope()
            else:
                self.validate_conditions(stmt.body, type_checker)

        elif isinstance(stmt, BlockStmt):
            if stmt.scope is not None:
                type_checker.symbol_table.enter_existing_scope(stmt.scope)
                try:
                    for s in stmt.statements:
                        self.validate_conditions(s, type_checker)
                finally:
                    type_checker.symbol_table.exit_scope()
            else:
                for s in stmt.statements:
                    self.validate_conditions(s, type_checker)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def is_bool_type(self, type_node: TypeNode) -> bool:
        """Check if type is bool.

        Args:
            type_node: Type node to check

        Returns:
            True if type is bool
        """
        return isinstance(type_node, PrimitiveType) and type_node.name == 'bool'

    def get_type_name(self, type_node: TypeNode) -> str:
        """Get the name of a type node.

        Args:
            type_node: Type node

        Returns:
            Type name as string
        """
        if isinstance(type_node, PrimitiveType):
            return type_node.name
        elif isinstance(type_node, FunctionType):
            return "function"
        else:
            return "unknown"

    def format_type(self, type_node: TypeNode) -> str:
        """Format a type node for error messages.

        Args:
            type_node: Type node to format

        Returns:
            Formatted type string
        """
        if isinstance(type_node, PrimitiveType):
            return type_node.name
        elif isinstance(type_node, FunctionType):
            param_types = ", ".join(self.format_type(p) for p in type_node.param_types)
            return f"({param_types}) -> {self.format_type(type_node.return_type)}"
        else:
            return "unknown"
