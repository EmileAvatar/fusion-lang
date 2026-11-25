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
from .stack_arrays import check_stack_arrays
from .currency import add_currency_module
from .many_dims import (add_dimension_enum, add_storage_enum, add_rounding_enum, check_many_dims_uses, mark_storage_calls,
                        name_parameter_sizes)
from .struct_parents import expand_struct_parents
from .inferred import check_set_once
from .class_rules import check_class_cycles, check_constructors
from .statics import expand_statics, static_setup_order
from .setup_blocks import expand_setup_blocks
from .readonly import check_readonly, check_readonly_calls, check_readonly_values
from .null_guards import check_surely_null, expand_null_guards
from .heap_arrays import mark_heap_arrays
from .generics import take_generic_functions, variadic_parameters
from .interfaces import check_interfaces
from .case_names import check_case_names
from .ownership import check_ownership

# [memory] assignment when no setting is given: "move" since Task 48.9 (D.102)
DEFAULT_ASSIGNMENT = 'move'
from .setup_blocks import check_collection_options
from .inheritance import expand_inheritance
from .class_rules import check_visibility_written, check_copy_fields
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
                 conditions_config=None, visibility_config=None, interfaces_config=None, source_config=None, memory_config=None,
                 collections_config=None, arrays_config=None, generics_config=None, ranges_config=None):
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
        self.not_around_guard = getattr(conditions_config, 'not_around_guard', False)   # 52.7
        # [modules] variables (Task 44.1): module-level variables allowed (default true)
        self.module_variables_allowed = bool(getattr(modules_config, 'variables', True))
        # [visibility] required (Task 32.2h): the level must be written everywhere
        self.visibility_required = bool(getattr(visibility_config, 'required', False))
        # [interfaces] defaultMethods (Task 32.5a, D.006): an interface's function may have code
        self.default_methods = bool(getattr(interfaces_config, 'default_methods', False))
        # [memory] assignment (Task 48.1): "move" - use after a move is an error
        self.assignment = getattr(memory_config, 'assignment', DEFAULT_ASSIGNMENT)
        self.move_field_out = getattr(memory_config, 'move_field_out', False)
        # [source] caseSensitive (Task 32.11): false - names differing only in case are errors
        self.case_sensitive = bool(getattr(source_config, 'case_sensitive', True))
        # [collections] allowChangeWhileLooping (Task 32.4, D.058)
        self.type_checker.allow_change_while_looping = bool(
            getattr(collections_config, 'allow_change_while_looping', False))
        # [arrays] stackWarn / stackLimit (Task 45.13, D.145) - in bytes
        self.stack_warn = getattr(arrays_config, 'stack_warn', 16 * 1024)
        self.stack_limit = getattr(arrays_config, 'stack_limit', 64 * 1024)
        # [arrays] order (Task 45.12, D.148): "columns" - the outer dimension first; "rows"
        self.type_checker.array_order = getattr(arrays_config, 'order', 'columns')
        # [arrays] csvManyDimensions (45.11b, D.151): toCSV on 3 dimensions or more
        self.type_checker.csv_many_dimensions = getattr(arrays_config, 'csv_many_dimensions', True)
        # [generics] enabled (Task 33, D.168): generics of the program's own
        self.generics_enabled = getattr(generics_config, 'enabled', True)
        self.shared_statics = getattr(generics_config, 'shared_statics', False)   # 33.3c (D.173)
        # [ranges] strictStep (Task 33.2g, D.170): a step that misses the end - a warning, or an error
        self.type_checker.strict_step = getattr(ranges_config, 'strict_step', False)
        self.control_flow_validator = ControlFlowValidator()
        self.entry_point_validator = EntryPointValidator()

        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []
        self.functions_registered = False

    def register_generic_instance(self, instance) -> None:
        """A copy of a generic function (Task 33.2a), made while another function is being checked:
        its name goes in the global scope; the function loop checks its body when it reaches it."""
        scope = self.symbol_table.current_scope
        self.symbol_table.current_scope = self.symbol_table.global_scope
        try:
            self.name_resolver.register_function(instance)
        finally:
            self.symbol_table.current_scope = scope

    def struct_instance(self, generic, kinds, location=None):
        """The copy of a generic struct for these types (Task 33.2b) - made once, registered and checked
        as the struct pass does for every struct. With `location` (a type written - `Box<Aircraft>`) its
        conditions are checked here (33.2d); a call checks them itself."""
        from .generics import struct_instance
        if location is not None:
            unmet = self.type_checker.unmet_condition(generic, dict(zip(generic.type_params, kinds)))
            if unmet:
                self.errors.append(SemanticError(unmet, location))
        key = tuple(self.type_checker.type_to_string(k) for k in kinds)
        if getattr(generic, 'made_early', False) and key not in generic.instances:
            # its copies are made before inheritance (33.3b) - from the types written in the program
            shown = f"{generic.name}<{', '.join(key)}>"
            self.errors.append(SemanticError(
                f"'{generic.name}' builds on a generic parent or interface - write its types where it is used: "
                f"{shown} x = {generic.name}(...) (33.3b)", location or generic.location))
        return struct_instance(self.program, generic, kinds, key, self._register_struct_instance)

    def _register_struct_instance(self, struct) -> None:
        scope = self.symbol_table.current_scope
        self.symbol_table.current_scope = self.symbol_table.global_scope
        try:
            self.name_resolver.register_struct(struct)
            self.name_resolver.check_struct(struct)
            self.type_checker.visit(struct)
            for field in struct.fields:
                self.type_checker._check_collection_type(field.field_type, field.location)
            if self.functions_registered:        # else the function pass registers them (33.2c)
                for method in struct.methods + list(getattr(struct, 'static_methods', None) or []):
                    self.name_resolver.register_function(method)
        finally:
            self.symbol_table.current_scope = scope

    @classmethod
    def for_project(cls, project_config) -> 'SemanticAnalyzer':
        """An analyzer with every setting of the project (main.py, and --interface - 33.7)."""
        if project_config is None:
            return cls()
        c = project_config
        return cls(structs_config=c.structs, strings_config=c.strings, stdlib_config=c.stdlib,
                   errors_config=c.errors, numbers_config=c.numbers, modules_config=c.modules,
                   conditions_config=c.conditions, visibility_config=c.visibility,
                   interfaces_config=c.interfaces, source_config=c.source, memory_config=c.memory,
                   collections_config=c.collections, arrays_config=c.arrays, generics_config=c.generics,
                   ranges_config=c.ranges)

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

        if not self.case_sensitive:       # 32.11 - the names as written, before any rewrite
            self.errors.extend(check_case_names(ast))

        # The Currency module (47.2b, D.186): Currency.fusion added when money is used - first, so every
        # pass after this treats it as the program's own class
        add_currency_module(ast)

        # The null guard (Task 52.8): c?.name, c?.f(), a ?? b rewritten into `is not null`,
        # `and`, `? :` and `if` - before anything else looks at the program
        guard_errors, guard_warnings = expand_null_guards(ast, self.not_around_guard)
        self.errors.extend(guard_errors)
        self.warnings.extend(guard_warnings)

        # Pass 0: string templates (Task 29.3) - every use becomes a format() call or a
        # lambda, before anything else looks at the program
        template_errors, template_warnings, template_spots = expand_templates(ast)
        self.errors.extend(template_errors)
        self.warnings.extend(template_warnings)

        # Structs building on structs (Task 32.8): Employee gets its Person part as a field
        # A generic class building on a generic one (33.3b): its copies made now, before inheritance
        from .generics import instantiate_early
        self.errors.extend(instantiate_early(ast, self.shared_statics))
        parent_errors, parent_warnings = expand_struct_parents(ast)
        self.errors.extend(parent_errors)
        self.warnings.extend(parent_warnings)
        # A class's statics (Task 32.2c): module variables and a set-up function per class
        self.errors.extend(expand_statics(ast))
        # Form B on any variable (Task 32.2d): a local's set-up block runs right after it
        self.errors.extend(expand_setup_blocks(ast))
        mark_storage_calls(ast)         # m.setStorage(...) right after its declaration (45.15, D.147)
        # Inheritance (Task 32.7): fields, functions, virtual ones, super - before interfaces
        self.errors.extend(expand_inheritance(ast))
        # Plain arrays that get a new size live on the heap (Task 45.10, D.141)
        mark_heap_arrays(ast)
        name_parameter_sizes(ast)       # int[][] m - its sizes passed hidden (45.12c)
        # Interfaces (Task 32.5a): what each needs, which class function answers it
        self.errors.extend(check_interfaces(ast, self.default_methods))

        # Pass 0: enums (Task 25) - turn enum types, values and calls into enum nodes, so
        # nothing after this mistakes an enum for a struct
        self.errors.extend(normalize_errors(ast))     # Task 26
        add_dimension_enum(ast)                  # ROWS / COLUMNS / DEPTH, when used (45.12d)
        add_storage_enum(ast)                    # FLAT / RECT / JAGG, when used (45.15)
        add_rounding_enum(ast)                   # halfEven / halfUp / down / up / exact, when used (47.8)
        self.errors.extend(normalize_enums(ast))
        self.errors.extend(check_holding_loops(ast))
        # Generic functions (Task 33.2a, D.166): taken out of the program - a copy is made for each
        # set of types used, when the type checker finds the call
        self.errors.extend(variadic_parameters(ast))     # f(int... numbers) - a List inside (33.2e)
        self.errors.extend(take_generic_functions(ast, self.generics_enabled, self.shared_statics))
        self.type_checker.program = ast
        self.type_checker.generic_host = self
        self.name_resolver.generic_host = self
        self.program = ast
        from .symbol import Symbol
        for name, generic in ast.generic_structs.items():         # Pair(1, "a"), Pair<int, string> (33.2b)
            try:
                self.symbol_table.define(Symbol(name=name, symbol_type='generic_struct', data_type=None,
                                                location=generic.location, declaration=generic))
            except SemanticError as e:
                self.errors.append(e)

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
        from .generics import check_condition_declarations
        self.errors.extend(check_condition_declarations(ast))       # <T extends Vehicle> (33.2d)
        structs = [d for d in ast.declarations if isinstance(d, StructDecl)]
        for struct in structs:
            self.type_checker.visit(struct)
            for field in struct.fields:   # List<...> fields (Task 18.5)
                self.type_checker._check_collection_type(field.field_type, field.location)
                inner = field.field_type
                while isinstance(inner, (ArrayType, ListType)):
                    inner = inner.element_type
                # A struct may hold an object (user, 2026-11-01 - D.097): null until set,
                # shared when the struct is copied
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
        self.functions_registered = True
        from .symbol import Symbol
        for name, generic in ast.generic_functions.items():      # first(...) - a copy when used (33.2a)
            try:
                self.symbol_table.define(Symbol(name=name, symbol_type='generic_function', data_type=None,
                                                location=generic.location, declaration=generic))
            except SemanticError as e:
                self.errors.append(e)

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
                    # Where it is - who may use an internal member (Task 32.2h)
                    self.type_checker.current_place = (getattr(decl, 'module_id', ''),
                                                       getattr(decl, 'namespace', None))
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
        # readonly parameters: never changed, passed on to a change or kept (Task 32.2e)
        self.errors.extend(check_readonly(ast))
        stack_errors, stack_warnings = check_stack_arrays(ast, self.stack_warn, self.stack_limit)   # 45.13
        self.errors.extend(check_many_dims_uses(ast))         # many dimensions: what 45.12a can't do yet
        self.errors.extend(stack_errors)
        self.warnings.extend(stack_warnings)
        self.errors.extend(check_readonly_calls(ast))      # f(readonly acc) (Task 48.3)
        self.errors.extend(check_surely_null(                      # Task 52.7 (D.117)
            ast, lambda t: self.type_checker.is_class(t) or type(t).__name__ == 'EnumType',
            self.type_checker.is_default_type))
        value_errors, value_warnings = check_readonly_values(ast)   # Task 50.1 / 50.2
        self.errors.extend(value_errors)
        self.warnings.extend(value_warnings)
        self.errors.extend(check_copy_fields(ast))       # nocopy / noshare (Task 32.5b)
        self.errors.extend(check_collection_options(ast))   # readOnly / noNull (Task 32.14)
        if self.assignment == 'move':                        # Task 48.1
            self.errors.extend(check_ownership(ast, self.move_field_out))
        if self.visibility_required:                    # Task 32.2h
            self.errors.extend(check_visibility_written(ast))
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
        self._generic_names_as_written(ast)
        return len(self.errors) == 0

    def _generic_names_as_written(self, ast) -> None:
        """A message names a generic's copy as the developer wrote it: `Box__int` -> `Box<int>` (33.2c)."""
        import re
        shown = {}
        for generic in list(getattr(ast, 'generic_structs', {}).values()) + \
                list(getattr(ast, 'generic_functions', {}).values()):
            for key, instance in (getattr(generic, 'instances', None) or {}).items():
                shown[instance.name] = f"{generic.name}<{', '.join(key)}>"
        if not shown:
            return
        pattern = re.compile(r'\b(' + '|'.join(re.escape(n) for n in sorted(shown, key=len, reverse=True)) + r')\b')
        for error in self.errors + self.warnings:
            message = pattern.sub(lambda m: shown[m.group(1)], error.message)
            if message != error.message:
                error.message = message
                error.args = (error._format_message(),)

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
