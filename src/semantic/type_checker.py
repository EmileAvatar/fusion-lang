"""Type checking for the Fusion semantic analyzer.

This module implements type checking to validate type compatibility in expressions,
assignments, function calls, and return statements.
"""

from typing import Optional, List
from src.parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    BreakStmt, ContinueStmt, ExpressionStmt, BlockStmt,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr, CallExpr, LambdaExpr, NamedArgument,
    InterpolatedStringExpr, StringExprPart, StringPositionalPart, ArrayLiteralExpr, IndexExpr, MemberExpr,
    StructDecl, StructField, TypeNode, PrimitiveType, FunctionType, ArrayType, StructType
)
from src.config.project_config import StructsConfig
from .symbol_table import SymbolTable
from .symbol import Symbol
from .errors import SemanticError
from src.lexer.token import SourceLocation


# Marks a struct field that has no written default but can still be left out of a
# constructor: an array or struct field starts with its own defaults (Task 18.2.3)
IMPLICIT_DEFAULT = object()


def field_default(field: StructField):
    """The default for a struct field in a constructor call: its written default, the
    IMPLICIT_DEFAULT marker for an array or struct field, or None if it must be given."""
    if field.default_value is not None:
        return field.default_value
    if isinstance(field.field_type, (ArrayType, StructType)):
        return IMPLICIT_DEFAULT
    return None


class TypeChecker:
    """Type checks the AST using visitor pattern.

    Validates type compatibility in expressions, assignments, function calls,
    and return statements. Collects all type errors and returns them for reporting.

    Attributes:
        symbol_table: Symbol table for looking up variable/function types
        current_function_return_type: Expected return type of current function
        errors: List of semantic errors found during type checking
        warnings: List of warnings (e.g. a long string in a struct field, Task 18.2.1)
        structs_config: The project's [structs] settings (fusion.toml)
    """

    def __init__(self, symbol_table: SymbolTable, structs_config: Optional[StructsConfig] = None):
        """Initialize type checker.

        Args:
            symbol_table: Symbol table for symbol lookup
            structs_config: The project's [structs] settings - defaults if not given
        """
        self.symbol_table = symbol_table
        self.current_function_return_type: Optional[TypeNode] = None
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []
        self.structs_config = structs_config or StructsConfig()

        # The interpolated string passed directly to print() - the only place one can be
        # used until strings can be built at run time (Task 15.10 / 18.3)
        self.print_interpolation: Optional[InterpolatedStringExpr] = None

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

        For expression nodes (anything with an `inferred_type` field), the resolved type
        is also written back onto the node itself, so later compiler stages - the code
        generator in particular - can read the type instead of re-deriving or guessing it.
        See taskSummary2.md Task 12.1/12.2.

        Args:
            node: AST node to visit

        Returns:
            Type of the expression, or None for statements

        Raises:
            NotImplementedError: If no visitor method exists for node type
        """
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_visit)
        result = method(node)
        if isinstance(result, TypeNode) and hasattr(node, 'inferred_type'):
            node.inferred_type = result
        return result

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

        # Arrays: element types compatible (allowing numeric promotion), and sizes match
        # if both are known (an unresolved size, still None, is treated as "don't know
        # yet" rather than a mismatch)
        if isinstance(expected, ArrayType) and isinstance(actual, ArrayType):
            if not self.types_compatible(expected.element_type, actual.element_type):
                return False
            if expected.size is not None and actual.size is not None:
                return expected.size == actual.size
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

        if isinstance(type1, ArrayType) and isinstance(type2, ArrayType):
            return self.types_equal(type1.element_type, type2.element_type) and \
                type1.size == type2.size

        # Structs: same struct, by name (Task 18.2.1)
        if isinstance(type1, StructType) and isinstance(type2, StructType):
            return type1.name == type2.name

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
            return PrimitiveType(location=type1.location, name='void')

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
        if isinstance(type_node, ArrayType):
            size_str = str(type_node.size) if type_node.size is not None else ''
            return f"{self.type_to_string(type_node.element_type)}[{size_str}]"
        if isinstance(type_node, StructType):
            return type_node.name
        return "unknown"

    def struct_declaration(self, type_node: TypeNode) -> Optional[StructDecl]:
        """The StructDecl for a struct type, looked up by name (Task 18.2.1) - or None if
        the type isn't a known struct. Looked up rather than read from type_node.declaration
        so it works no matter which pass created the type node."""
        if not isinstance(type_node, StructType):
            return None
        symbol = self.symbol_table.global_scope.lookup(type_node.name)
        if symbol is not None and symbol.symbol_type == 'struct':
            return symbol.declaration
        return None

    def check_string_field_value(self, struct_name: str, field: StructField, value: ASTNode) -> None:
        """Apply the project's string-length rules to a value going into a string field
        (Task 18.2.1, [structs] in fusion.toml):

        - longer than string_warn_length: kept in full, with a warning (a guideline only)
        - longer than string_max_length: cut to that length, with a warning - the only
          place a string is ever cut ("max memory" = no limit)

        Only a string literal's length is known at compile time. Strings can't be built or
        changed at run time yet (Task 18.3), when the same rules will be checked at run time.
        The cut is done here, on the literal itself, so codegen emits the shortened text.
        """
        if not (isinstance(field.field_type, PrimitiveType) and field.field_type.name == 'string'):
            return
        if not (isinstance(value, LiteralExpr) and value.type_hint == 'string'):
            return
        length = len(value.value)
        max_length = self.structs_config.string_max_length
        warn_length = self.structs_config.string_warn_length
        if max_length is not None and length > max_length:
            value.value = value.value[:max_length]
            self.warnings.append(SemanticError(
                f"String for field '{field.name}' of struct '{struct_name}' has {length} "
                f"characters - cut to the project's string_max_length of {max_length}",
                value.location
            ))
        elif warn_length and length > warn_length:
            self.warnings.append(SemanticError(
                f"String for field '{field.name}' of struct '{struct_name}' has {length} "
                f"characters (the project's string_warn_length guideline is {warn_length}) - "
                f"kept in full",
                value.location
            ))

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

        if symbol.symbol_type == 'struct':
            self.errors.append(SemanticError(
                f"'{node.name}' is a struct type, not a value - create one with "
                f"{node.name}(...)",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        # A named function used as a value, e.g. apply(tripler, 5) (Task 18.1.3)
        if symbol.symbol_type == 'function':
            if not isinstance(symbol.declaration, FunctionDecl):
                self.errors.append(SemanticError(
                    f"Built-in function '{node.name}' can't be used as a value",
                    node.location
                ))
            elif any(isinstance(p.param_type, ArrayType) for p in symbol.declaration.parameters):
                self.errors.append(SemanticError(
                    f"Function '{node.name}' has array parameters, so it can't be used as a "
                    f"value yet",
                    node.location
                ))
        return symbol.data_type

    def _check_function_type_supported(self, type_node: TypeNode, location) -> None:
        """Reject function types v1 can't lower to C (Task 18.1.3): an array parameter
        needs a hidden length argument, which a plain function value can't carry yet."""
        if isinstance(type_node, FunctionType):
            for param_type in type_node.parameter_types:
                if isinstance(param_type, ArrayType):
                    self.errors.append(SemanticError(
                        "Function types can't have array parameters yet",
                        location
                    ))
                self._check_function_type_supported(param_type, location)
            self._check_function_type_supported(type_node.return_type, location)

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
                # Except structs: comparing them is part of 18.3's equality-operator design,
                # and C can't compare structs with == at all (Task 18.2.1)
                for operand, operand_type in ((node.left, left_type), (node.right, right_type)):
                    if isinstance(operand_type, StructType):
                        self.errors.append(SemanticError(
                            f"Comparing structs with '{node.operator}' is not supported yet - "
                            f"compare their fields instead (struct equality comes with Task "
                            f"18.3)",
                            operand.location
                        ))
                        break
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
        return PrimitiveType(location=node.location, name='void')

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
        return PrimitiveType(location=node.location, name='void')

    def visit_CallExpr(self, node: CallExpr) -> TypeNode:
        """Check function call argument types.

        Args:
            node: Call expression node

        Returns:
            Return type of the function
        """
        # Calling the result of an expression, e.g. (func(int x) : x * 2)(5) (Task 18.1.3)
        if not isinstance(node.callee, IdentifierExpr):
            callee_type = self.visit(node.callee)
            if self._reject_named_arguments(node, "a function value"):
                return callee_type.return_type if isinstance(callee_type, FunctionType) else \
                    PrimitiveType(location=node.location, name='void')
            return self._check_function_value_call(node, callee_type, "function value")

        func_name = node.callee.name

        # Look up function
        symbol = self.symbol_table.lookup(func_name)
        if not symbol:
            self.errors.append(SemanticError(
                f"Undefined function: '{func_name}'",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        if symbol.symbol_type == 'struct':
            struct = symbol.declaration
            if self._has_named_arguments(node):
                self._check_named_call(
                    node, f"struct '{struct.name}'", 'field',
                    [(f.name, f.field_type, field_default(f)) for f in struct.fields], struct=struct)
                node.callee_declaration = struct
                return StructType(location=node.location, name=struct.name, declaration=struct)
            return self._check_struct_construction(node, struct)

        if symbol.symbol_type != 'function':
            # A variable or parameter holding a function (Task 18.1.3)
            if isinstance(symbol.data_type, FunctionType):
                node.callee.inferred_type = symbol.data_type
                if self._reject_named_arguments(node, f"'{func_name}' (a function variable)"):
                    return symbol.data_type.return_type
                return self._check_function_value_call(node, symbol.data_type, f"'{func_name}'")
            self.errors.append(SemanticError(
                f"'{func_name}' is not a function",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        # Get function type
        func_type = symbol.data_type
        if not isinstance(func_type, FunctionType):
            return PrimitiveType(location=node.location, name='void')

        # Named arguments (Task 18.2.2) need the declared parameter names - builtins have none
        declaration = symbol.declaration if isinstance(symbol.declaration, FunctionDecl) else None
        if self._has_named_arguments(node):
            if declaration is None:
                self._reject_named_arguments(node, f"built-in function '{func_name}'")
                return func_type.return_type
            self._check_named_call(
                node, f"'{func_name}'", 'parameter',
                [(p.name, p.param_type, p.default_value) for p in declaration.parameters],
                func_name=func_name)
            node.callee_declaration = declaration
            return func_type.return_type

        # print(text, ...) - extra arguments fill {@1}, {@2}, ... placeholders (Task 18.2.2b)
        if func_name == 'print' and node.arguments:
            return self._check_print_call(node, func_type)

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

        # Special case for len(): accepts exactly one array argument, of any element type.
        # The registered FunctionType's parameter type is just a placeholder (see
        # register_builtins in name_resolver.py) since the type system has no generics -
        # this is where the actual argument type is checked instead.
        if func_name == 'len':
            if len(node.arguments) != 1:
                self.errors.append(SemanticError(
                    f"Function 'len' expects 1 argument, got {len(node.arguments)}",
                    node.location
                ))
                return func_type.return_type
            arg_type = self.visit(node.arguments[0])
            if not isinstance(arg_type, ArrayType):
                self.errors.append(SemanticError(
                    f"Function 'len' expects an array, got {self.type_to_string(arg_type)}",
                    node.arguments[0].location
                ))
            return func_type.return_type

        # Trailing parameters with defaults may be omitted (Task 18.1.1)
        defaults = [p.default_value for p in declaration.parameters] if declaration else []
        expected_count = len(func_type.parameter_types)
        required_count = sum(1 for d in defaults if d is None) if declaration else expected_count
        actual_count = len(node.arguments)
        if actual_count < required_count or actual_count > expected_count:
            if required_count == expected_count:
                expected_text = f"{expected_count} argument(s)"
            else:
                expected_text = f"{required_count} to {expected_count} arguments"
            self.errors.append(SemanticError(
                f"Function '{func_name}' expects {expected_text}, got {actual_count}",
                node.location
            ))
            return func_type.return_type

        # C has no default arguments - record the full argument list for codegen, with each
        # omitted argument replaced by its parameter's (constant) default value
        node.resolved_arguments = list(node.arguments) + defaults[actual_count:]
        # A direct call to a declared function - codegen reads its parameters from here
        node.callee_declaration = declaration

        # An interpolated string can only be print's own argument (Task 15.10)
        if func_name == 'print' and node.arguments and isinstance(node.arguments[0], InterpolatedStringExpr):
            self.print_interpolation = node.arguments[0]

        # Check each argument type
        for i, (arg, expected_type) in enumerate(zip(node.arguments, func_type.parameter_types)):
            actual_type = self.visit(arg)
            if isinstance(expected_type, ArrayType):
                self._check_array_argument(func_name, i, arg, expected_type, actual_type)
            elif not self.types_compatible(expected_type, actual_type):
                self.errors.append(SemanticError(
                    f"Argument {i+1} to '{func_name}': expected {self.type_to_string(expected_type)}, "
                    f"got {self.type_to_string(actual_type)}",
                    arg.location
                ))

        return func_type.return_type

    def _check_print_call(self, node: CallExpr, func_type: FunctionType) -> TypeNode:
        """Check print(text, arg1, arg2, ...) (Task 18.2.2b).

        The text's {@N} placeholders refer to the arguments after it, by number from 1 - in
        any order and as often as wanted. Every argument must be printable. An argument that
        no placeholder uses is only a warning: a translated message may leave one out.

        Returns:
            print's return type (void)
        """
        text, extras = node.arguments[0], node.arguments[1:]

        # An interpolated string can only be print's own argument (Task 15.10)
        if isinstance(text, InterpolatedStringExpr):
            self.print_interpolation = text
        text_type = self.visit(text)
        string_type = func_type.parameter_types[0]
        if not self.types_compatible(string_type, text_type):
            self.errors.append(SemanticError(
                f"Argument 1 to 'print': expected {self.type_to_string(string_type)}, got "
                f"{self.type_to_string(text_type)}",
                text.location
            ))

        positions = []
        if isinstance(text, InterpolatedStringExpr):
            positions = [s.index for s in text.segments if isinstance(s, StringPositionalPart)]

        if extras and not positions:
            self.errors.append(SemanticError(
                f"print() was given {len(extras)} argument(s) after its text, but the text has "
                f"no {{@1}}-style placeholders to use them",
                node.location
            ))
        for index in sorted(set(positions)):
            if index < 1:
                self.errors.append(SemanticError(
                    f"{{@{index}}} isn't a valid placeholder - they start at {{@1}}",
                    text.location
                ))
            elif index > len(extras):
                self.errors.append(SemanticError(
                    f"{{@{index}}} has no matching argument - print() was given {len(extras)} "
                    f"argument(s) after its text",
                    text.location
                ))

        for number, extra in enumerate(extras, start=1):
            extra_type = self.visit(extra)
            if not isinstance(extra_type, PrimitiveType):
                self.errors.append(SemanticError(
                    f"Can't print a whole {self.type_to_string(extra_type)} value - print its "
                    f"elements or fields one at a time",
                    extra.location
                ))
            if positions and number not in positions:
                self.warnings.append(SemanticError(
                    f"Argument {number + 1} to print() isn't used - no {{@{number}}} placeholder "
                    f"in the text",
                    extra.location
                ))

        node.resolved_arguments = list(node.arguments)
        return func_type.return_type

    @staticmethod
    def _has_named_arguments(node: CallExpr) -> bool:
        return any(isinstance(arg, NamedArgument) for arg in node.arguments)

    def _reject_named_arguments(self, node: CallExpr, description: str) -> bool:
        """Report named arguments where they can't work (Task 18.2.2): builtins and calls
        through function values have no parameter names to match. Returns True (after
        visiting the argument values, for error recovery) if any were found."""
        if not self._has_named_arguments(node):
            return False
        for arg in node.arguments:
            if isinstance(arg, NamedArgument):
                self.errors.append(SemanticError(
                    f"Named argument '{arg.name}' can't be used when calling {description} - "
                    f"it has no parameter names to match; pass the arguments in order",
                    arg.location
                ))
            self.visit(arg.value if isinstance(arg, NamedArgument) else arg)
        return True

    def _check_named_call(self, node: CallExpr, owner: str, kind: str, slots: list,
                          func_name: str = None, struct: StructDecl = None) -> None:
        """Match a call's arguments to parameters (or struct fields) when some are named
        (Task 18.2.2): `createShip("Discovery", crew = 80)`, `Point(y = 4, x = 3)`.

        - positional arguments fill the first slots, in order, and must all come before any
          named argument
        - a named argument fills the slot with that name, in any order
        - any slot with a default may be left out - not only trailing ones
        - errors: unknown name, the same slot given twice, a slot with no default left out

        On success, node.resolved_arguments holds one value per slot in declaration order -
        what codegen emits, since C has no named arguments.

        Args:
            node: The call
            owner: How to name the callee in messages ("'f'" or "struct 'Point'")
            kind: 'parameter' or 'field'
            slots: (name, type, default_value) per parameter/field, in declaration order
            func_name: The function's name, for array-argument checks
            struct: The struct being constructed, for string-field length rules
        """
        names = [name for name, _, _ in slots]
        bound = [None] * len(slots)
        bound_by_name = [False] * len(slots)
        ok = True
        seen_named = False
        # Sentence-start form of the owner, for messages that begin with it
        owner_title = owner[0].upper() + owner[1:]

        def fail(message, location, value):
            nonlocal ok
            ok = False
            self.errors.append(SemanticError(message, location))
            self.visit(value)  # still type-check it, for error recovery

        for position, arg in enumerate(node.arguments):
            if isinstance(arg, NamedArgument):
                seen_named = True
                if arg.name not in names:
                    fail(f"{owner_title} has no {kind} named '{arg.name}' (its {kind}s: "
                         f"{', '.join(names)})", arg.location, arg.value)
                elif bound[names.index(arg.name)] is not None:
                    how = "" if bound_by_name[names.index(arg.name)] else " (by position and by name)"
                    fail(f"{kind.capitalize()} '{arg.name}' of {owner} is given twice{how}",
                         arg.location, arg.value)
                else:
                    bound[names.index(arg.name)] = arg.value
                    bound_by_name[names.index(arg.name)] = True
            elif seen_named:
                fail(f"Argument {position + 1} to {owner} has no name but comes after a named "
                     f"argument - arguments without names must come first", arg.location, arg)
            elif position >= len(slots):
                fail(f"{owner_title} has {len(slots)} {kind}(s), got an argument {position + 1}",
                     arg.location, arg)
            else:
                bound[position] = arg

        # A missing slot is only worth reporting when every argument matched - after an
        # unknown or misplaced one, "missing" is usually just a side effect of that mistake
        all_matched = ok
        for index, (name, _, default) in enumerate(slots):
            if all_matched and bound[index] is None and default is None:
                ok = False
                self.errors.append(SemanticError(
                    f"Missing argument for {kind} '{name}' of {owner}", node.location))

        for index, value in enumerate(bound):
            if value is None:
                continue
            name, expected_type, _ = slots[index]
            actual_type = self.visit(value)
            if isinstance(expected_type, ArrayType) and func_name is not None:
                self._check_array_argument(func_name, index, value, expected_type, actual_type)
            elif isinstance(expected_type, ArrayType) and struct is not None:
                if not self._check_array_field_value(struct, struct.fields[index], value, actual_type):
                    ok = False
            elif not self.types_compatible(expected_type, actual_type):
                ok = False
                self.errors.append(SemanticError(
                    f"Argument '{name}' to {owner}: expected "
                    f"{self.type_to_string(expected_type)}, got {self.type_to_string(actual_type)}",
                    value.location
                ))
            if struct is not None:
                self.check_string_field_value(struct.name, struct.fields[index], value)

        if ok:
            # An omitted array/struct field stays None: codegen gives it its own defaults
            node.resolved_arguments = [
                value if value is not None
                else (None if slots[index][2] is IMPLICIT_DEFAULT else slots[index][2])
                for index, value in enumerate(bound)
            ]

    def _check_struct_construction(self, node: CallExpr, struct: StructDecl) -> TypeNode:
        """Check a generated struct constructor call: Point(3, 4) (Task 18.2.1).

        Arguments are matched to fields in declaration order. A field with a default - or an
        array or struct field, which starts with its own defaults (18.2.3) - can be left off
        when no field after it is given, so every field up to the last one without a default
        is required. Same int -> float promotion as function arguments.

        Returns:
            The struct type
        """
        struct_type = StructType(location=node.location, name=struct.name, declaration=struct)
        fields = struct.fields
        required = max((i + 1 for i, f in enumerate(fields) if field_default(f) is None), default=0)
        actual_count = len(node.arguments)

        if actual_count < required or actual_count > len(fields):
            if required == len(fields):
                expected_text = f"{len(fields)} argument(s)"
            else:
                expected_text = f"{required} to {len(fields)} arguments"
            self.errors.append(SemanticError(
                f"Struct '{struct.name}' expects {expected_text} (one per field, in order: "
                f"{', '.join(f.name for f in fields)}), got {actual_count}",
                node.location
            ))
            for arg in node.arguments:
                self.visit(arg)
            return struct_type

        for i, (arg, field) in enumerate(zip(node.arguments, fields)):
            actual_type = self.visit(arg)
            if isinstance(field.field_type, ArrayType):
                self._check_array_field_value(struct, field, arg, actual_type)
            elif not self.types_compatible(field.field_type, actual_type):
                self.errors.append(SemanticError(
                    f"Argument {i+1} to '{struct.name}' (field '{field.name}'): expected "
                    f"{self.type_to_string(field.field_type)}, got "
                    f"{self.type_to_string(actual_type)}",
                    arg.location
                ))
            self.check_string_field_value(struct.name, field, arg)

        # C needs every field - fill in the omitted fields' defaults, as for function calls
        node.resolved_arguments = list(node.arguments) + [f.default_value for f in fields[actual_count:]]
        node.callee_declaration = struct
        return struct_type

    def _check_array_field_value(self, struct: StructDecl, field: StructField, value: ASTNode,
                                 actual_type: TypeNode) -> bool:
        """Check the value given for an array field in a constructor (Task 18.2.3).

        Like initializing an array variable, it must be an array literal of exactly the
        field's size - C can't initialize one array from another, and whether that should
        copy or share is still undecided (see _check_array_var_decl).

        Returns:
            True if the value is acceptable
        """
        expected: ArrayType = field.field_type

        def error(message: str) -> bool:
            self.errors.append(SemanticError(
                f"Field '{field.name}' of struct '{struct.name}': {message}", value.location))
            return False

        if not isinstance(value, ArrayLiteralExpr):
            return error(f"needs an array literal here (e.g. [1, 2, 3]) - copying an existing "
                         f"array into a field isn't supported yet; set its elements one by one")
        if len(value.elements) != expected.size:
            return error(f"expected {expected.size} element(s), got {len(value.elements)}")
        if value.elements and not self.types_compatible(expected.element_type, actual_type.element_type):
            return error(f"expected elements of type {self.type_to_string(expected.element_type)}, "
                         f"got {self.type_to_string(actual_type.element_type)}")
        return True

    @staticmethod
    def _root_variable(expr: ASTNode) -> Optional[IdentifierExpr]:
        """The variable at the base of `a`, `a.b[i].c`, ... - or None if it isn't a variable
        (e.g. a function's return value). Used for const checks (Task 18.2.3)."""
        while isinstance(expr, (MemberExpr, IndexExpr)):
            expr = expr.object if isinstance(expr, MemberExpr) else expr.array
        return expr if isinstance(expr, IdentifierExpr) else None

    def check_struct_nesting(self, structs: List[StructDecl]) -> None:
        """Check how deeply structs nest, against the project's [structs] settings (Task
        18.2.3), and reject a struct that contains itself.

        Depth counts levels of structs: plain fields only = 1; holding a struct of depth 1 =
        2, and so on. An array of structs counts like one struct. Each problem is reported
        once, on the struct where it starts, rather than on every struct that contains it.
        """
        by_name = {s.name: s for s in structs}

        def children(struct):
            for field in struct.fields:
                field_type = field.field_type
                if isinstance(field_type, ArrayType):
                    field_type = field_type.element_type
                if isinstance(field_type, StructType) and field_type.name in by_name:
                    yield field_type.name

        # A struct containing itself (directly or through others) would be infinitely large
        finished, reported, found_cycle = set(), set(), False

        def walk(name, path):
            nonlocal found_cycle
            if name in finished:
                return
            if name in path:
                cycle = path[path.index(name):] + [name]
                found_cycle = True
                key = frozenset(cycle)
                if key not in reported:
                    reported.add(key)
                    self.errors.append(SemanticError(
                        f"Struct '{name}' contains itself ({' -> '.join(cycle)}) - a struct "
                        f"can't hold itself, directly or through other structs, because it "
                        f"would be infinitely large",
                        by_name[name].location
                    ))
                return
            path.append(name)
            for child in children(by_name[name]):
                walk(child, path)
            path.pop()
            finished.add(name)

        for name in by_name:
            walk(name, [])
        if found_cycle:
            return  # depth is meaningless for a cycle

        chains = {}

        def chain(name):
            """The deepest nesting chain starting at this struct, e.g. [Scene, Shape, Point]."""
            if name not in chains:
                deepest = max((chain(c) for c in children(by_name[name])), key=len, default=[])
                chains[name] = [name] + deepest
            return chains[name]

        max_depth = self.structs_config.max_nesting_depth
        warn_depth = self.structs_config.warn_nesting_depth
        for struct in structs:
            path = chain(struct.name)
            depth = len(path)
            child_depth = depth - 1
            if depth > max_depth and child_depth <= max_depth:
                self.errors.append(SemanticError(
                    f"Struct '{struct.name}' is nested {depth} levels deep "
                    f"({' -> '.join(path)}) - the project allows {max_depth} "
                    f"([structs] max_nesting_depth in fusion.toml)",
                    struct.location
                ))
            elif warn_depth and warn_depth <= depth <= max_depth and child_depth < warn_depth:
                self.warnings.append(SemanticError(
                    f"Struct '{struct.name}' is nested {depth} levels deep "
                    f"({' -> '.join(path)}) - the project warns from {warn_depth} levels "
                    f"([structs] warn_nesting_depth in fusion.toml)",
                    struct.location
                ))

    def _check_function_value_call(self, node: CallExpr, callee_type: TypeNode,
                                   description: str) -> TypeNode:
        """Check a call through a function value - a variable, parameter, or expression
        holding a function (Task 18.1.3). A function value carries only its type, so every
        argument must be given (no defaults).

        Returns:
            The function's return type (void for error recovery)
        """
        if not isinstance(callee_type, FunctionType):
            self.errors.append(SemanticError(
                f"Cannot call a value of type {self.type_to_string(callee_type)}",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        expected_count = len(callee_type.parameter_types)
        if len(node.arguments) != expected_count:
            self.errors.append(SemanticError(
                f"Calling {description} expects {expected_count} argument(s), got "
                f"{len(node.arguments)}",
                node.location
            ))
            return callee_type.return_type

        for i, (arg, expected_type) in enumerate(zip(node.arguments, callee_type.parameter_types)):
            actual_type = self.visit(arg)
            if not self.types_compatible(expected_type, actual_type):
                self.errors.append(SemanticError(
                    f"Argument {i+1} to {description}: expected "
                    f"{self.type_to_string(expected_type)}, got {self.type_to_string(actual_type)}",
                    arg.location
                ))
        node.resolved_arguments = list(node.arguments)
        return callee_type.return_type

    def _check_array_argument(self, func_name: str, index: int, arg: ASTNode,
                              expected: ArrayType, actual: TypeNode) -> None:
        """Check an argument passed to an array parameter (Task 18.1.2).

        Arrays are passed by reference - the function works on the caller's array - so the
        rules are stricter than for assignment:
        - element types must match exactly: no int -> float promotion, since C can't read
          an int array's memory as floats
        - an `int[5]` parameter needs an argument whose size is known to be 5; an `int[]`
          parameter accepts any size (its length is passed alongside it)
        - a const array can't be passed, because the function could change its elements
          (a read-only parameter form doesn't exist yet)
        """
        def error(message: str) -> None:
            self.errors.append(SemanticError(f"Argument {index+1} to '{func_name}': {message}",
                                             arg.location))

        if not isinstance(actual, ArrayType):
            error(f"expected {self.type_to_string(expected)}, got {self.type_to_string(actual)}")
            return
        if isinstance(arg, ArrayLiteralExpr) and not arg.elements:
            error("an empty array literal can't be passed")
            return
        if not self.types_equal(expected.element_type, actual.element_type):
            error(f"expected an array of {self.type_to_string(expected.element_type)}, got an "
                  f"array of {self.type_to_string(actual.element_type)} (array element types "
                  f"must match exactly)")
            return
        if expected.size is not None:
            if actual.size is None:
                error(f"expected an array of exactly {expected.size} elements, but this "
                      f"array's size is only known at run time")
                return
            if actual.size != expected.size:
                error(f"expected an array of exactly {expected.size} elements, got "
                      f"{actual.size}")
                return
        root = self._root_variable(arg)
        if root is not None:
            symbol = self.symbol_table.lookup(root.name)
            if symbol and symbol.is_constant:
                what = f"const array '{root.name}'" if root is arg else \
                    f"an array inside const '{root.name}'"
                error(f"{what} can't be passed to a function, because the function could change "
                      f"its elements")

    def visit_NamedArgument(self, node: NamedArgument) -> TypeNode:
        """A named argument's type is its value's type. Normally reached only through
        _check_named_call / _reject_named_arguments, which visit the value directly."""
        return self.visit(node.value)

    def visit_LambdaExpr(self, node: LambdaExpr) -> TypeNode:
        """Check lambda expression.

        Args:
            node: Lambda expression node

        Returns:
            Function type of the lambda
        """
        # Re-enter the lambda's own scope (populated by the name resolver), so its
        # parameters are visible in the body
        if node.scope is not None:
            self.symbol_table.enter_existing_scope(node.scope)
        old_return_type = self.current_function_return_type
        try:
            for param in node.parameters:
                if isinstance(param.param_type, ArrayType):
                    self.errors.append(SemanticError(
                        f"Lambda parameter '{param.name}' can't be an array yet",
                        param.location
                    ))
                self.visit(param)

            # The return type isn't written in the source: infer it from a single-expression
            # body (Task 18.1.3). A block body (built directly as an AST, not parsed) keeps
            # any return type it was given, or is void
            self.current_function_return_type = node.return_type
            body_type = self.visit(node.body)
            if node.return_type is None:
                if isinstance(node.body, BlockStmt) or body_type is None:
                    node.return_type = PrimitiveType(location=node.location, name='void')
                else:
                    node.return_type = body_type
        finally:
            self.current_function_return_type = old_return_type
            if node.scope is not None:
                self.symbol_table.exit_scope()

        return FunctionType(
            parameter_types=[param.param_type for param in node.parameters],
            return_type=node.return_type,
            location=node.location
        )

    def visit_InterpolatedStringExpr(self, node: InterpolatedStringExpr) -> TypeNode:
        """Check interpolated string expression.

        Args:
            node: Interpolated string expression node

        Returns:
            String type
        """
        # Until strings can be built at run time (Task 18.3), an interpolated string only
        # works as print's own argument - anywhere else it used to pass this check and then
        # produce invalid C (`char* s = "x is %d", x;`) - Task 15.10
        if node is not self.print_interpolation:
            self.errors.append(SemanticError(
                "A string with {...} values can only be passed directly to print() for now - "
                "building strings while the program runs comes with Task 18.3",
                node.location
            ))

        # Type check each interpolated expression segment (this also populates each
        # expression's inferred_type, which the code generator reads to pick the
        # correct format specifier - see Task 12.3)
        for segment in node.segments:
            if isinstance(segment, StringExprPart):
                expr_type = self.visit(segment.expression)
                # Only single values can be printed - a whole array (Task 15.9, used to crash
                # codegen), struct, or function has no printf format. (void is the error-
                # recovery type - its own error, e.g. an undefined variable, is already
                # reported)
                if not isinstance(expr_type, PrimitiveType):
                    self.errors.append(SemanticError(
                        f"Can't print a whole {self.type_to_string(expr_type)} value - print "
                        f"its elements or fields one at a time",
                        segment.expression.location
                    ))

        return PrimitiveType(location=node.location, name='string')

    def visit_ArrayLiteralExpr(self, node: ArrayLiteralExpr) -> TypeNode:
        """Check array literal and infer its element type.

        Args:
            node: Array literal expression node

        Returns:
            ArrayType with the inferred element type and the literal's length. An empty
            literal's element type is unknown ('void') until matched against a declared
            array type in visit_VarDeclStmt.
        """
        if not node.elements:
            return ArrayType(
                location=node.location,
                element_type=PrimitiveType(location=node.location, name='void'),
                size=0
            )

        element_types = [self.visit(el) for el in node.elements]
        result_type = element_types[0]

        for i, elem_type in enumerate(element_types[1:], start=1):
            if self.is_numeric_type(result_type) and self.is_numeric_type(elem_type):
                result_type = self.get_wider_type(result_type, elem_type)
            elif not self.types_equal(result_type, elem_type):
                self.errors.append(SemanticError(
                    f"Array elements must have consistent types: element 0 is "
                    f"{self.type_to_string(result_type)}, element {i} is "
                    f"{self.type_to_string(elem_type)}",
                    node.elements[i].location
                ))

        return ArrayType(
            location=node.location,
            element_type=result_type,
            size=len(node.elements)
        )

    def visit_IndexExpr(self, node: IndexExpr) -> TypeNode:
        """Check array index expression: arr[i]

        Args:
            node: Index expression node

        Returns:
            The array's element type (void for error recovery if the target isn't an array)
        """
        array_type = self.visit(node.array)
        index_type = self.visit(node.index)

        if not isinstance(array_type, ArrayType):
            self.errors.append(SemanticError(
                f"Cannot index non-array type '{self.type_to_string(array_type)}'",
                node.array.location
            ))
            return PrimitiveType(location=node.location, name='void')

        if not (isinstance(index_type, PrimitiveType) and index_type.name == 'int'):
            self.errors.append(SemanticError(
                f"Array index must be int, got {self.type_to_string(index_type)}",
                node.index.location
            ))

        return array_type.element_type

    def visit_MemberExpr(self, node: MemberExpr) -> TypeNode:
        """Check struct field access: point.x (Task 18.2.1)

        Returns:
            The field's type (void for error recovery)
        """
        object_type = self.visit(node.object)
        struct = self.struct_declaration(object_type)
        if struct is None:
            self.errors.append(SemanticError(
                f"Cannot read field '{node.member}' of a value of type "
                f"{self.type_to_string(object_type)} - only structs have fields",
                node.location
            ))
            return PrimitiveType(location=node.location, name='void')

        for field in struct.fields:
            if field.name == node.member:
                return field.field_type

        self.errors.append(SemanticError(
            f"Struct '{struct.name}' has no field '{node.member}' (its fields: "
            f"{', '.join(f.name for f in struct.fields)})",
            node.location
        ))
        return PrimitiveType(location=node.location, name='void')

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
        if isinstance(node.var_type, ArrayType):
            self._check_array_var_decl(node)
            return

        if isinstance(node.var_type, FunctionType):
            self._check_function_type_supported(node.var_type, node.location)
            # No null functions yet - calling one would crash (nullability is Task 14)
            if node.initializer is None:
                self.errors.append(SemanticError(
                    f"Function variable '{node.name}' must be initialized with a function",
                    node.location
                ))
                return

        if node.initializer:
            init_type = self.visit(node.initializer)
            if not self.types_compatible(node.var_type, init_type):
                self.errors.append(SemanticError(
                    f"Cannot assign {self.type_to_string(init_type)} to variable of type {self.type_to_string(node.var_type)}",
                    node.location
                ))

    def _check_array_var_decl(self, node: VarDeclStmt) -> None:
        """Check an array variable declaration and resolve its size if not given explicitly.

        Fixed-size arrays only (Task 9 v1): the size must come from an explicit `[N]` in
        the type, an array literal initializer, or both (in which case they must agree).
        If the type didn't specify a size, it's set here from the initializer's length -
        the same "mutate the shared type node in place" pattern used for `inferred_type`.

        Args:
            node: Variable declaration statement node (node.var_type is an ArrayType)
        """
        array_type: ArrayType = node.var_type

        if not node.initializer:
            if array_type.size is None:
                self.errors.append(SemanticError(
                    f"Array '{node.name}' must specify a size (e.g. "
                    f"{self.type_to_string(array_type.element_type)}[5]) or be initialized "
                    "with an array literal",
                    node.location
                ))
            return

        init_type = self.visit(node.initializer)
        if not isinstance(init_type, ArrayType):
            self.errors.append(SemanticError(
                f"Cannot initialize array '{node.name}' with non-array value of type "
                f"{self.type_to_string(init_type)}",
                node.location
            ))
            return

        # Only an array literal can initialize an array. `int[] b = a` used to pass this
        # check and then fail in GCC ("invalid initializer"), since C can't initialize one
        # array from another - and whether it should copy or share is an undecided design
        # question, more pressing now that array parameters exist (Task 18.1.2)
        if not isinstance(node.initializer, ArrayLiteralExpr):
            self.errors.append(SemanticError(
                f"Array '{node.name}' must be initialized with an array literal (e.g. "
                f"[1, 2, 3]) - initializing an array from another array isn't supported yet; "
                f"copy the elements one by one",
                node.location
            ))
            return

        if array_type.size is None:
            array_type.size = init_type.size
        elif init_type.size is not None and array_type.size != init_type.size:
            self.errors.append(SemanticError(
                f"Array '{node.name}' declared with size {array_type.size} but initializer "
                f"has {init_type.size} element(s)",
                node.location
            ))

        # Skip the element-type check for an empty literal - there's nothing to compare
        if init_type.size and not self.types_compatible(array_type.element_type, init_type.element_type):
            self.errors.append(SemanticError(
                f"Cannot initialize {self.type_to_string(array_type.element_type)}[] with "
                f"elements of type {self.type_to_string(init_type.element_type)}",
                node.location
            ))

    def visit_AssignmentStmt(self, node: AssignmentStmt) -> None:
        """Check assignment type compatibility.

        Assignment target is either a plain variable (IdentifierExpr) or an array element
        (IndexExpr, e.g. arr[i] = value) - Task 9 v1 does not support reassigning an array
        as a whole (arr = [...] after declaration), since a C array isn't assignable that
        way once declared; only per-element assignment is allowed.

        Args:
            node: Assignment statement node
        """
        if isinstance(node.target, IdentifierExpr):
            self._check_identifier_assignment(node)
        elif isinstance(node.target, IndexExpr):
            self._check_index_assignment(node)
        elif isinstance(node.target, MemberExpr):
            self._check_member_assignment(node)
        else:
            self.errors.append(SemanticError(
                "Assignment target must be an identifier, array index, or struct field",
                node.target.location
            ))

    def _check_identifier_assignment(self, node: AssignmentStmt) -> None:
        """Check assignment to a plain variable: x = value"""
        target_name = node.target.name

        symbol = self.symbol_table.lookup(target_name)
        if not symbol:
            self.errors.append(SemanticError(
                f"Undefined variable: '{target_name}'",
                node.location
            ))
            return

        if isinstance(symbol.data_type, ArrayType):
            self.errors.append(SemanticError(
                f"Cannot reassign array '{target_name}' as a whole - assign to individual "
                f"elements instead (e.g. {target_name}[i] = value)",
                node.location
            ))
            return

        if symbol.is_constant:
            self.errors.append(SemanticError(
                f"Cannot assign to constant: '{target_name}'",
                node.location
            ))

        value_type = self.visit(node.value)
        if not self.types_compatible(symbol.data_type, value_type):
            self.errors.append(SemanticError(
                f"Cannot assign {self.type_to_string(value_type)} to variable of type {self.type_to_string(symbol.data_type)}",
                node.location
            ))

    def _check_index_assignment(self, node: AssignmentStmt) -> None:
        """Check assignment to an array element: arr[i] = value"""
        target: IndexExpr = node.target

        # visit_IndexExpr validates the array/index types and returns the element type
        element_type = self.visit(target)

        # The array may be a variable, or a field of one (`p.scores[0] = 1`, Task 18.2.3)
        root = self._root_variable(target.array)
        if root is not None:
            array_symbol = self.symbol_table.lookup(root.name)
            if array_symbol and array_symbol.is_constant:
                if root is target.array:
                    message = f"Cannot assign to element of constant array '{root.name}'"
                else:
                    message = f"Cannot assign to an element of an array inside constant '{root.name}'"
                self.errors.append(SemanticError(message, node.location))

        value_type = self.visit(node.value)
        if not self.types_compatible(element_type, value_type):
            self.errors.append(SemanticError(
                f"Cannot assign {self.type_to_string(value_type)} to array element of type "
                f"{self.type_to_string(element_type)}",
                node.location
            ))

    def _check_member_assignment(self, node: AssignmentStmt) -> None:
        """Check assignment to a struct field: point.x = value (Task 18.2.1)

        The struct must be stored in a variable (not, say, a function's return value, which
        C can't assign into), which must not be const. A string field can't be changed after
        construction when the project sets [structs] string_mutable = false.
        """
        target: MemberExpr = node.target
        field_type = self.visit(target)

        if isinstance(field_type, ArrayType):
            self.errors.append(SemanticError(
                f"Cannot assign array field '{target.member}' as a whole - assign its elements "
                f"instead (e.g. ...{target.member}[i] = value)",
                node.location
            ))
            return

        root = self._root_variable(target.object)
        if root is None:
            self.errors.append(SemanticError(
                f"Can only assign to field '{target.member}' of a struct stored in a variable",
                node.location
            ))
        else:
            symbol = self.symbol_table.lookup(root.name)
            if symbol and symbol.is_constant:
                self.errors.append(SemanticError(
                    f"Cannot assign to field '{target.member}' of constant '{root.name}'",
                    node.location
                ))

        struct = self.struct_declaration(getattr(target.object, 'inferred_type', None))
        field = next((f for f in struct.fields if f.name == target.member), None) if struct else None
        if field is not None and isinstance(field_type, PrimitiveType) and field_type.name == 'string' \
                and not self.structs_config.string_mutable:
            self.errors.append(SemanticError(
                f"String field '{field.name}' of struct '{struct.name}' can't be changed after "
                f"the struct is created - the project sets [structs] string_mutable = false",
                node.location
            ))

        value_type = self.visit(node.value)
        if not self.types_compatible(field_type, value_type):
            self.errors.append(SemanticError(
                f"Cannot assign {self.type_to_string(value_type)} to field '{target.member}' "
                f"of type {self.type_to_string(field_type)}",
                node.location
            ))
        if field is not None:
            self.check_string_field_value(struct.name, field, node.value)

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

        # Note: the loop variable lives in its own scope (node.scope, populated by
        # NameResolver - see Task 12.6), one level above the body's own block scope. No
        # explicit enter/exit needed here: node.body is a BlockStmt, and visit_BlockStmt
        # reuses node.body.scope, whose .parent chain already includes this for-scope -
        # that's enough for lookup_recursive to find the loop variable from inside the body.

        # Check body
        self.visit(node.body)

    def visit_BlockStmt(self, node: BlockStmt) -> None:
        """Check all statements in block.

        Block scoping (Task 12.6): reuses the exact Scope object NameResolver already
        created and populated for this block (node.scope), so lookups here see the same
        symbols NameResolver saw, without redeclaring anything. Falls back to creating a
        fresh scope if node.scope is unset, which happens when code constructs/type-checks
        a BlockStmt directly without running NameResolver first (some unit tests do); the
        fresh scope still chains to whatever the caller's current scope is via `parent`,
        so lookups to anything already in scope keep working.

        Args:
            node: Block statement node
        """
        if node.scope is not None:
            self.symbol_table.enter_existing_scope(node.scope)
        else:
            self.symbol_table.enter_scope(f"block:{id(node)}")

        try:
            for stmt in node.statements:
                self.visit(stmt)
        finally:
            self.symbol_table.exit_scope()

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
        self._check_function_type_supported(node.param_type, node.location)

        # Check default value type if present
        if node.default_value:
            default_type = self.visit(node.default_value)
            if not self.types_compatible(node.param_type, default_type):
                self.errors.append(SemanticError(
                    f"Default value type {self.type_to_string(default_type)} does not match parameter type {self.type_to_string(node.param_type)}",
                    node.location
                ))

    def visit_StructDecl(self, node: StructDecl) -> None:
        """Check a struct's field defaults (Task 18.2.1): each must suit its field's type,
        and string defaults follow the project's string-length rules."""
        for field in node.fields:
            # Array and struct fields can't have defaults - already reported by the name
            # resolver, so don't add a second, type-mismatch error (Task 18.2.3)
            if field.default_value is None or isinstance(field.field_type, (ArrayType, StructType)):
                continue
            default_type = self.visit(field.default_value)
            if not self.types_compatible(field.field_type, default_type):
                self.errors.append(SemanticError(
                    f"Default value for field '{field.name}' of struct '{node.name}': expected "
                    f"{self.type_to_string(field.field_type)}, got "
                    f"{self.type_to_string(default_type)}",
                    field.default_value.location
                ))
            self.check_string_field_value(node.name, field, field.default_value)

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Check program (handled by check_program).

        Args:
            node: Program node
        """
        for decl in node.declarations:
            self.visit(decl)
