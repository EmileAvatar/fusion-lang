"""
Entry Point Validator for Fusion Programming Language

This module validates program entry point (main function):
- Ensures main function exists
- Validates main function signature
- Detects duplicate main functions
"""

from typing import List, Tuple
from src.parser.ast_nodes import *
from src.lexer.token import SourceLocation


class SemanticError(Exception):
    """Semantic analysis error with source location."""

    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location
        super().__init__(f"{message} at {location}")


class EntryPointValidator:
    """Validates program entry point (main function) structure."""

    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []

    def validate_program(self, program: ProgramNode) -> Tuple[List[SemanticError], List[SemanticError]]:
        """Validate program structure.

        Args:
            program: The program AST root node

        Returns:
            Tuple of (errors, warnings)
        """
        self.errors = []
        self.warnings = []

        main_functions = []

        # Find all main functions
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl) and decl.name == 'main':
                main_functions.append(decl)

        # Check for missing main
        if len(main_functions) == 0:
            # Use program location if available, otherwise create a generic one
            location = program.location if hasattr(program, 'location') else SourceLocation(
                filename='<program>',
                line=1,
                column=1
            )
            self.errors.append(SemanticError(
                "Program must have a 'main' function",
                location
            ))
            return self.errors, self.warnings

        # Check for multiple main functions
        if len(main_functions) > 1:
            for func in main_functions[1:]:
                self.errors.append(SemanticError(
                    "Multiple 'main' functions defined",
                    func.location
                ))
            return self.errors, self.warnings

        # Validate main signature
        main_func = main_functions[0]
        self.validate_main_signature(main_func)

        return self.errors, self.warnings

    def validate_main_signature(self, func: FunctionDecl) -> None:
        """Validate main function signature.

        Allowed signatures (MVP):
        - void function main()
        - int function main()

        Future (not MVP):
        - void function main(string[] args)
        - int function main(string[] args)

        Args:
            func: Main function declaration node
        """
        # Check return type (must be void or int)
        if isinstance(func.return_type, PrimitiveType):
            if func.return_type.name not in ['void', 'int']:
                self.errors.append(SemanticError(
                    f"main function must return 'void' or 'int', got '{func.return_type.name}'",
                    func.location
                ))
        else:
            self.errors.append(SemanticError(
                "main function return type must be 'void' or 'int'",
                func.location
            ))

        # Check parameters (MVP: must be empty)
        if len(func.parameters) > 0:
            self.warnings.append(SemanticError(
                "main function parameters are not supported in MVP (ignored)",
                func.location
            ))
            # Note: This is a warning for now; future versions will support args

    # ========================================================================
    # Additional Validations (Optional/Future)
    # ========================================================================

    def check_top_level_statements(self, program: ProgramNode) -> None:
        """Check for orphaned top-level statements (future feature).

        In MVP, only function declarations are allowed at top level.
        This is already enforced by the parser.

        Args:
            program: The program AST root node
        """
        # This is a placeholder for future validation
        # Parser already only allows FunctionDecl at top level
        pass

    def validate_import_order(self, program: ProgramNode) -> None:
        """Ensure imports come before declarations (future feature).

        Args:
            program: The program AST root node
        """
        # This is a placeholder for Phase 4+ when imports are supported
        pass
