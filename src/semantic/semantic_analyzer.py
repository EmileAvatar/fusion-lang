"""Semantic analyzer for Fusion programs.

This module provides the main SemanticAnalyzer class that orchestrates
all semantic analysis passes over the AST.
"""

import sys
from typing import List

from ..parser.ast_nodes import ProgramNode, BlockStmt
from .errors import SemanticError
from .symbol_table import SymbolTable
from .name_resolver import NameResolver
from .type_checker import TypeChecker
from .control_flow_validator import ControlFlowValidator
from .entry_point_validator import EntryPointValidator


class SemanticAnalyzer:
    """Main semantic analyzer that orchestrates all validation passes.

    The analyzer performs semantic analysis in the following order:
    1. Entry point validation (check for main function)
    2. Name resolution (build symbol table)
    3. Type checking (validate types)
    4. Control flow validation (validate returns, loops)

    Attributes:
        symbol_table: Symbol table for name resolution
        name_resolver: Name resolution pass
        type_checker: Type checking pass
        control_flow_validator: Control flow validation pass
        entry_point_validator: Entry point validation pass
        errors: List of errors found during analysis
        warnings: List of warnings found during analysis
    """

    def __init__(self):
        """Initialize the semantic analyzer with all validation passes."""
        self.symbol_table = SymbolTable()
        self.name_resolver = NameResolver(self.symbol_table)
        self.type_checker = TypeChecker(self.symbol_table)
        self.control_flow_validator = ControlFlowValidator()
        self.entry_point_validator = EntryPointValidator()

        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []

    def analyze(self, ast: ProgramNode) -> bool:
        """Analyze the AST and return True if no errors.

        Performs semantic analysis in the following order:
        1. Entry point validation (check for main)
        2. Register all functions in global scope
        3. For each function:
           a. Resolve names in function body
           b. Type check function body
           c. Control flow check function

        Args:
            ast: The program AST to analyze

        Returns:
            True if analysis succeeded (no errors), False otherwise
        """
        # Clear previous results
        self.errors.clear()
        self.warnings.clear()

        # Pass 1: Validate entry point
        ep_errors, ep_warnings = self.entry_point_validator.validate_program(ast)
        self.errors.extend(ep_errors)
        self.warnings.extend(ep_warnings)

        # Pass 2: Register all function declarations (global scope only)
        from src.parser.ast_nodes import FunctionDecl
        for decl in ast.declarations:
            if isinstance(decl, FunctionDecl):
                self.name_resolver.register_function(decl)

        # Pass 3: For each function, resolve + type check + control flow check
        # while inside the function scope
        for decl in ast.declarations:
            if isinstance(decl, FunctionDecl):
                # Enter function scope
                self.symbol_table.enter_scope(f"function:{decl.name}")

                try:
                    # Register parameters
                    for param in decl.parameters:
                        self.name_resolver.register_parameter(param)

                    # Resolve names in function body. If it's a block (the normal case -
                    # lambdas can have a single expression body instead), it shares the
                    # parameter scope directly rather than nesting a new one underneath -
                    # see NameResolver.resolve_block's new_scope docstring (Task 12.6).
                    if decl.body:
                        if isinstance(decl.body, BlockStmt):
                            self.name_resolver.resolve_block(decl.body, new_scope=False)
                        else:
                            self.name_resolver.resolve_statement(decl.body)

                    # Type check function (already in scope)
                    old_return_type = self.type_checker.current_function_return_type
                    self.type_checker.current_function_return_type = decl.return_type

                    for param in decl.parameters:
                        self.type_checker.visit(param)

                    if decl.body:
                        self.type_checker.visit(decl.body)

                    self.type_checker.current_function_return_type = old_return_type

                    # Control flow check function
                    self.control_flow_validator.validate_function(decl, self.type_checker)

                finally:
                    # Always exit scope
                    try:
                        self.symbol_table.exit_scope()
                    except:
                        pass

        # Collect errors from each component
        self.errors.extend(self.name_resolver.errors)
        self.errors.extend(self.type_checker.errors)
        self.errors.extend(self.control_flow_validator.errors)
        self.warnings.extend(self.control_flow_validator.warnings)

        # Return success if no errors
        return len(self.errors) == 0

    def get_errors(self) -> List[SemanticError]:
        """Get all collected errors.

        Returns:
            A copy of the error list
        """
        return self.errors.copy()

    def get_warnings(self) -> List[SemanticError]:
        """Get all collected warnings.

        Returns:
            A copy of the warning list
        """
        return self.warnings.copy()

    def print_diagnostics(self) -> None:
        """Print all errors and warnings to stderr."""
        for error in self.errors:
            print(f"Error: {error}", file=sys.stderr)

        for warning in self.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

        if self.errors:
            print(f"\n{len(self.errors)} error(s) found", file=sys.stderr)
        if self.warnings:
            print(f"{len(self.warnings)} warning(s) found", file=sys.stderr)
