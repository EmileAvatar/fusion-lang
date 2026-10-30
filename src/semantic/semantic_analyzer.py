"""Semantic analyzer for Fusion programs.

This module provides the main SemanticAnalyzer class that orchestrates
all semantic analysis passes over the AST.
"""

import sys
from typing import List, Optional

from ..parser.ast_nodes import (ProgramNode, BlockStmt, StructDecl, PrimitiveType, EnumDecl,
                                ErrorDecl, LiteralExpr, VarDeclStmt, ArrayType, ArrayLiteralExpr,
                                ListType, MapType)
from .enums import normalize_enums, check_holding_loops
from .templates import expand_templates
from .struct_parents import expand_struct_parents
from .inferred import check_set_once
from .class_rules import check_class_cycles, check_constructors
from .statics import expand_statics, static_setup_order
from .setup_blocks import expand_setup_blocks
from .error_rules import normalize_errors, check_error_settings, marked_but_cannot_fail
from ..config.project_config import StructsConfig, StringsConfig
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

    def __init__(self, structs_config: Optional[StructsConfig] = None,
                 strings_config: Optional[StringsConfig] = None, stdlib_config=None,
                 errors_config=None, numbers_config=None, modules_config=None,
                 conditions_config=None):
        """Initialize the semantic analyzer with all validation passes.

        Args:
            structs_config: The project's [structs] settings from fusion.toml (Task 18.2) -
                defaults if not given
        """
        self.structs_config = structs_config or StructsConfig()
        self.errors_config = errors_config   # [errors] returns / exceptions (Task 26.5)
        self.symbol_table = SymbolTable()
        self.name_resolver = NameResolver(self.symbol_table)
        self.type_checker = TypeChecker(self.symbol_table, self.structs_config, strings_config,
                                        stdlib_config)
        # [numbers] auto_widening (Task 27.2f): an int used as a float
        self.type_checker.auto_widening = bool(getattr(numbers_config, 'auto_widening', False))
        # [conditions] numbers (Task 30.9): numbers in if / while conditions
        self.type_checker.number_conditions = getattr(conditions_config, 'numbers', 'positive')
        # [modules] variables (Task 44.1): module-level variables allowed (default true)
        self.module_variables_allowed = bool(getattr(modules_config, 'variables', True))
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

        # Pass 0: string templates (Task 29.3) - every use becomes a format() call or a
        # lambda, before anything else looks at the program
        template_errors, template_warnings, template_spots = expand_templates(ast)
        self.errors.extend(template_errors)
        self.warnings.extend(template_warnings)

        # Structs building on structs (Task 32.8): Employee gets its Person part as a field
        parent_errors, parent_warnings = expand_struct_parents(ast)
        self.errors.extend(parent_errors)
        self.warnings.extend(parent_warnings)
        # A class's statics (Task 32.2c): module variables and a set-up function per class
        self.errors.extend(expand_statics(ast))
        # Form B on any variable (Task 32.2d): a local's set-up block runs right after it
        self.errors.extend(expand_setup_blocks(ast))

        # Pass 0: enums (Task 25) - turn enum types, values and calls into enum nodes, so
        # nothing after this mistakes an enum for a struct
        self.errors.extend(normalize_errors(ast))     # Task 26
        self.errors.extend(normalize_enums(ast))
        self.errors.extend(check_holding_loops(ast))

        # Pass 1: Validate entry point
        ep_errors, ep_warnings = self.entry_point_validator.validate_program(ast)
        self.errors.extend(ep_errors)
        self.warnings.extend(ep_warnings)

        # Pass 2: Register all struct declarations, check their fields, then register all
        # function declarations (global scope only) - structs first, so any signature can
        # use any struct (Task 18.2.1)
        from src.parser.ast_nodes import FunctionDecl
        self.name_resolver.register_enums(ast)
        self.name_resolver.register_error_types(ast)   # Task 26.9
        self.name_resolver.register_structs(ast)
        structs = [d for d in ast.declarations if isinstance(d, StructDecl)]
        for struct in structs:
            self.type_checker.visit(struct)
            for field in struct.fields:   # List<...> fields (Task 18.5)
                self.type_checker._check_collection_type(field.field_type, field.location)
                inner = field.field_type
                while isinstance(inner, (ArrayType, ListType)):
                    inner = inner.element_type
                if not struct.is_class and getattr(self.type_checker.struct_declaration(inner),
                                                   'is_class', False):
                    self.errors.append(SemanticError(
                        f"Struct '{struct.name}' can't hold a class object (field '{field.name}') "
                        f"- a struct is a value; [structs] classes (planned) will allow it",
                        field.location))
                if field.by_ref and not isinstance(field.field_type, (ListType, MapType)):
                    self.errors.append(SemanticError(
                        f"byRef on field '{field.name}': only a List or Map field can be shared "
                        f"between copies of the struct", field.location))
        self.type_checker.check_struct_nesting([s for s in structs if not s.is_class])
        self.warnings.extend(check_class_cycles(structs))   # objects in a circle (32.10d)
        # A custom error type's fields (Task 26.9) - any type a struct field may have
        for decl in (d for d in ast.declarations if isinstance(d, ErrorDecl) and not d.builtin):
            for field in decl.fields:
                self.name_resolver.resolve_type(field.field_type)
                self.type_checker._check_collection_type(field.field_type, field.location)
                if field.default_value is not None and \
                        not self.name_resolver.is_constant_default(field.default_value):
                    self.errors.append(SemanticError(
                        f"The default of '{field.name}' in error type '{decl.name}' must be a "
                        f"constant", field.location))
            for what, value, want in (('message', decl.default_message, 'string'),
                                      ('code', decl.default_code, 'int')):
                if value is not None and not (isinstance(value, LiteralExpr) and value.type_hint == want):
                    self.errors.append(SemanticError(
                        f"The default {what} of error type '{decl.name}' must be a {want} "
                        f"written in the source", value.location))
        # The data an enum's values carry (Task 25.4) - any type a struct field may have
        for enum in (d for d in ast.declarations if isinstance(d, EnumDecl)):
            for variant in enum.variants:
                for field in variant.fields:
                    self.name_resolver.resolve_type(field.field_type)
                    self.type_checker._check_collection_type(field.field_type, field.location)
        self.check_structs_settings(structs)
        for decl in ast.declarations:
            if isinstance(decl, FunctionDecl):
                self.name_resolver.register_function(decl)

        # Module-level variables and constants (Task 44.1): checked in the order written, in
        # the global scope - an initializer may use the functions and the module variables
        # above it; every function sees them all
        for decl in ast.declarations:
            if isinstance(decl, VarDeclStmt):
                self.check_module_variable(decl)

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
                    self.type_checker.current_function_returns_error = decl.returns_error
                    self.type_checker._check_collection_type(decl.return_type, decl.location)

                    self.type_checker.current_function_name = decl.name
                    # Whose private members this function may use (Task 32.2a)
                    self.type_checker.current_class = getattr(decl, 'method_of', None)
                    if decl.name == 'main' and decl.parameters:
                        self.type_checker.require_layer('std', "main's arguments (string... args)",
                                                        decl.location)
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
        self.warnings.extend(self.type_checker.warnings)
        self.errors.extend(self.control_flow_validator.errors)
        self.warnings.extend(self.control_flow_validator.warnings)

        # Return success if no errors
        # Ways of handling errors the project turned off (Task 26.5)
        self.errors.extend(check_error_settings(ast, self.errors_config))
        # Classes set up in the order they depend on each other; a circle (Task 32.2c)
        self.errors.extend(static_setup_order(ast))
        # Constructors that can't be told apart, or call each other in a circle (32.2b)
        self.errors.extend(check_constructors(
            [d for d in ast.declarations if isinstance(d, StructDecl)],
            self.type_checker.type_to_string))
        # A let / var declared without a value: set before read, a let once (Task 46.1)
        known = {(str(e), str(e.location)) for e in self.errors}
        self.errors.extend(e for e in check_set_once(ast) if (str(e), str(e.location)) not in known)
        self.warnings.extend(marked_but_cannot_fail(ast))   # Task 26.7
        # A template called in several places repeats its text's errors - report each once;
        # where a template use was wrong, what follows from it isn't reported again (29.3)
        follow_on = {str(e.location) for e in template_errors}
        kept, seen = [], set()
        for error in self.errors:
            where = str(error.location)
            if error in template_errors or (where not in follow_on and where not in template_spots):
                kept.append(error)
            elif where in template_spots and where not in follow_on and str(error) not in seen:
                seen.add(str(error))
                kept.append(error)
        self.errors[:] = kept
        return len(self.errors) == 0

    def check_module_variable(self, decl: VarDeclStmt) -> None:
        """A variable or constant declared outside any function (Task 44.1)."""
        if not decl.is_const and decl.inferred != 'let' and not getattr(decl, 'is_static', False) \
                and not self.module_variables_allowed:
            self.errors.append(SemanticError(
                f"Module-level variable '{decl.name}': fusion.toml sets [modules] variables = "
                f"false (module-level constants are still allowed)", decl.location))
        if isinstance(decl.var_type, ArrayType) and decl.initializer is not None \
                and not isinstance(decl.initializer, ArrayLiteralExpr):
            self.errors.append(SemanticError(
                f"A module-level array needs a list of values ([1, 2, 3]) - '{decl.name}'",
                decl.location))
        self.name_resolver.resolve_var_decl(decl)
        symbol = self.symbol_table.global_scope.symbols.get(decl.name)
        if symbol is not None:
            symbol.module_variable = True
        self.type_checker.visit(decl)

    def check_structs_settings(self, structs: List[StructDecl]) -> None:
        """Report [structs] settings that need saying on every build (Task 18.2.1).

        - string_storage = "pooled" is accepted in fusion.toml but not built yet (Task 17) -
          an error only when the program actually has a string field it would apply to
        """
        location = structs[0].location if structs else None
        if not getattr(self.structs_config, 'functions', False):
            for struct in (s for s in structs if not s.is_class):    # a class always may
                for method in getattr(struct, 'methods', None) or []:
                    self.errors.append(SemanticError(
                        f"Struct '{struct.name}' has a method '{method.method_name}' - functions "
                        f"on structs are off; [structs] functions = true allows them",
                        method.location))
        if not self.structs_config.hold_collections:
            for struct in (s for s in structs if not s.is_class):
                for f in struct.fields:
                    if isinstance(f.field_type, (ListType, MapType)):
                        self.errors.append(SemanticError(
                            f"Field '{f.name}' of struct '{struct.name}' is a "
                            f"{'List' if isinstance(f.field_type, ListType) else 'Map'} - the "
                            f"project sets [structs] holdCollections = false", f.location))
        has_string_field = any(
            isinstance(f.field_type, PrimitiveType) and f.field_type.name == 'string'
            for s in structs for f in s.fields
        )
        if self.structs_config.string_storage == 'pooled' and has_string_field:
            self.errors.append(SemanticError(
                'fusion.toml sets [structs] stringStorage = "pooled", which is not '
                'implemented yet (Task 17) - use "owned"',
                location
            ))

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
