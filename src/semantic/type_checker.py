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
from src.config.project_config import StructsConfig, StringsConfig
from .symbol_table import SymbolTable
from .name_resolver import BUILTIN_DEFAULTS, INT_OR_TEXT_BUILTINS, builtin_defaults
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

    def __init__(self, symbol_table: SymbolTable, structs_config: Optional[StructsConfig] = None,
                 strings_config: Optional[StringsConfig] = None):
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
        self.strings_config = strings_config or StringsConfig()
        self.checked_literals = set()  # literals already checked against max_length

        # ids of interpolated strings that are print's or format's own text - the only place
        # {@N} placeholders can appear (Task 18.3.3)
        self.placeholder_texts = set()

        # ids of calls whose returned array is used in a supported way (Task 18.2.4) - see
        # visit_CallExpr
        self.allowed_array_calls = set()

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

    @staticmethod
    def _is_string_type(type_node: TypeNode) -> bool:
        return isinstance(type_node, PrimitiveType) and type_node.name == 'string'

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

        Only a string literal's length is known at compile time. The hard limit for every
        string is [strings] max_length (Task 18.3.4b - see visit_LiteralExpr).
        """
        if not (isinstance(field.field_type, PrimitiveType) and field.field_type.name == 'string'):
            return
        if not (isinstance(value, LiteralExpr) and value.type_hint == 'string'):
            return
        length = len(value.value)
        warn_length = self.structs_config.string_warn_length
        if warn_length and length > warn_length:
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

        # [strings] max_length applies to source text too (Task 18.3.4b): too long is an error,
        # never a cut
        max_length = self.strings_config.max_length
        if node.type_hint == 'string' and max_length is not None and len(str(node.value)) > max_length \
                and id(node) not in self.checked_literals:
            self.checked_literals.add(id(node))
            self.errors.append(SemanticError(
                f"String has {len(str(node.value))} characters, more than the project's "
                f"max_length of {max_length} ([strings] in fusion.toml)", node.location))

        # A project using ascii encoding can only hold ASCII text (Task 18.3.2b)
        if self.strings_config.encoding == 'ascii' and node.type_hint in ('string', 'char'):
            for ch in str(node.value):
                if ord(ch) > 0x7F:
                    self.errors.append(SemanticError(
                        f"{'String' if node.type_hint == 'string' else 'Char'} literal contains "
                        f"U+{ord(ch):04X}, but the project uses ascii encoding "
                        f"([strings] encoding = \"ascii\" in fusion.toml)",
                        node.location))
                    break
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
            elif isinstance(symbol.declaration.return_type, ArrayType):
                self.errors.append(SemanticError(
                    f"Function '{node.name}' returns an array, so it can't be used as a "
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
            if isinstance(type_node.return_type, ArrayType):
                self.errors.append(SemanticError(
                    "Function types can't return arrays yet",
                    location
                ))
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

        # Joining strings (Task 18.3.2): string + string, string + char, char + string.
        # Numbers are joined with interpolation instead ("{a}{b}") - never `"1" + 1`
        if node.operator == '+' and (self._is_string_type(left_type) or self._is_string_type(right_type)):
            joinable = ('string', 'char')
            for operand, operand_type in ((node.left, left_type), (node.right, right_type)):
                if not (isinstance(operand_type, PrimitiveType) and operand_type.name in joinable):
                    self.errors.append(SemanticError(
                        f"Can't join a string and {self.type_to_string(operand_type)} with '+' - "
                        f"use interpolation instead, e.g. \"{{name}}{{count}}\"",
                        operand.location
                    ))
            return PrimitiveType(location=node.location, name='string')

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

        # Equality operators (Task 18.3.5): ==, !=, ===, !==
        if node.operator in ['==', '!=', '===', '!==']:
            self._check_equality(node, left_type, right_type)
            return PrimitiveType(location=node.location, name='bool')

        # Comparison operators: comparable types -> bool
        if node.operator in ['<', '>', '<=', '>=']:
            if self._is_string_type(left_type) and self._is_string_type(right_type):
                pass  # strings order alphabetically (Task 18.3.1)
            else:
                # For ordering comparisons, require numeric types (or two strings)
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

    _NUMBER_TYPES = ('int', 'float', 'double')

    def _check_equality(self, node: BinaryExpr, left_type: TypeNode, right_type: TypeNode) -> None:
        """The equality operators (Task 18.3.5, user decisions 2026-10-07):

        - `==` / `!=` compare values, across types only through a small fixed table (see
          `_equality_problem`); any other pair is an error
        - `===` / `!==` also compare the type: on two different types the result is always
          the same, so it's a warning, and the node is marked `never_equal` for the generator
        """
        if self._is_void(left_type) or self._is_void(right_type):
            return  # an error was already reported for an operand
        strict = node.operator in ('===', '!==')
        if strict and not self._same_type_for_strict(left_type, right_type):
            node.never_equal = True
            always = 'false' if node.operator == '===' else 'true'
            self.warnings.append(SemanticError(
                f"'{node.operator}' is always {always} here: "
                f"{self.type_to_string(left_type)} and {self.type_to_string(right_type)} are "
                f"different types (use '==' to compare values across types)",
                node.location
            ))
            return
        problem = self._equality_problem(left_type, right_type)
        if problem:
            self.errors.append(SemanticError(
                f"Can't compare {self.type_to_string(left_type)} with "
                f"{self.type_to_string(right_type)} using '{node.operator}': {problem}",
                node.location
            ))

    @staticmethod
    def _is_void(type_node: TypeNode) -> bool:
        return isinstance(type_node, PrimitiveType) and type_node.name == 'void'

    def _same_type_for_strict(self, left: TypeNode, right: TypeNode) -> bool:
        """Same type for `===`: arrays only need the same element type - their sizes are
        compared when the program runs, like their elements."""
        if isinstance(left, ArrayType) and isinstance(right, ArrayType):
            return self._same_type_for_strict(left.element_type, right.element_type)
        return self.types_equal(left, right)

    def _equality_problem(self, left: TypeNode, right: TypeNode) -> Optional[str]:
        """None when `==` can compare the two types, else the reason it can't. Across types
        only: a number and text (numeric text equals the number), a char and a string (a
        one-character string equals the char), int / float / double by value. Never
        "truthiness": a bool only equals a bool."""
        if isinstance(left, PrimitiveType) and isinstance(right, PrimitiveType):
            names = (left.name, right.name)
            if all(n in self._NUMBER_TYPES for n in names):
                return None
            if left.name == right.name and left.name in ('string', 'char', 'bool'):
                return None
            if set(names) == {'string', 'char'}:
                return None
            if 'string' in names and any(n in self._NUMBER_TYPES for n in names):
                return None
            if 'bool' in names:
                return "a bool only equals a bool (no truthiness)"
            return "these types never compare equal - convert one first"
        if isinstance(left, ArrayType) and isinstance(right, ArrayType):
            if isinstance(left.element_type, ArrayType) or isinstance(right.element_type, ArrayType):
                return "arrays of arrays can't be compared yet"
            problem = self._equality_problem(left.element_type, right.element_type)
            return f"their elements can't be compared ({problem})" if problem else None
        if isinstance(left, StructType) and isinstance(right, StructType):
            left_struct, right_struct = self.struct_declaration(left), self.struct_declaration(right)
            if left_struct is None or right_struct is None:
                return "unknown struct"
            if [f.name for f in left_struct.fields] != [f.name for f in right_struct.fields]:
                return (f"structs {left_struct.name} and {right_struct.name} have different "
                        f"fields - they compare only with the same field names in the same order")
            for left_field, right_field in zip(left_struct.fields, right_struct.fields):
                problem = self._equality_problem(left_field.field_type, right_field.field_type)
                if problem:
                    return f"field '{left_field.name}' can't be compared ({problem})"
            return None
        if isinstance(left, FunctionType) or isinstance(right, FunctionType):
            return "functions can't be compared"
        return "these types never compare equal"

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

    # Where the array a function returns can be used (Task 18.2.4) - anywhere else, the
    # call is an error with this hint
    _ARRAY_CALL_USES = ("store it in a variable (int[3] a = make()), assign it to an array "
                        "(a = make()), index it directly (make()[0]), or return it")

    def _allow_array_call(self, expr: ASTNode) -> None:
        """Mark a call as being in a place where a returned array is supported."""
        if isinstance(expr, CallExpr):
            self.allowed_array_calls.add(id(expr))

    def visit_CallExpr(self, node: CallExpr) -> TypeNode:
        """Check a call, then check that a returned array is used in a supported place
        (Task 18.2.4). C returns the array inside a hidden struct, which can be copied into
        an array or indexed - but not passed on by reference or printed whole."""
        result = self._visit_call(node)
        if isinstance(result, ArrayType) and id(node) not in self.allowed_array_calls:
            name = node.callee.name if isinstance(node.callee, IdentifierExpr) else "this function"
            self.errors.append(SemanticError(
                f"The array returned by '{name}' can't be used here - {self._ARRAY_CALL_USES}",
                node.location
            ))
        return result

    def _visit_call(self, node: CallExpr) -> TypeNode:
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

        # print(text, ...) - extra arguments fill {@1}, {@2}, ... placeholders (Task 18.2.2b);
        # format(text, ...) builds the same text as a string (18.3.3)
        if func_name in ('print', 'format') and node.arguments:
            return self._check_print_call(node, func_type, func_name)

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
            if not isinstance(arg_type, ArrayType) and not self._is_string_type(arg_type):
                self.errors.append(SemanticError(
                    f"Function 'len' expects an array or a string, got "
                    f"{self.type_to_string(arg_type)}",
                    node.arguments[0].location
                ))
            return func_type.return_type

        # toString(x) - any single value: int, float, double, bool, char, string (18.3.2)
        if func_name == 'toString':
            if len(node.arguments) != 1:
                self.errors.append(SemanticError(
                    f"Function 'toString' expects 1 argument, got {len(node.arguments)}",
                    node.location))
                return func_type.return_type
            arg_type = self.visit(node.arguments[0])
            if not isinstance(arg_type, PrimitiveType) or arg_type.name == 'void':
                self.errors.append(SemanticError(
                    f"Function 'toString' expects a single value (int, float, double, bool, "
                    f"char or string), got {self.type_to_string(arg_type)}",
                    node.arguments[0].location))
            node.resolved_arguments = list(node.arguments)
            return func_type.return_type

        # Trailing parameters with defaults may be omitted (Task 18.1.1) - for a built-in,
        # its optional arguments (Task 18.3.6)
        expected_count = len(func_type.parameter_types)
        if declaration:
            defaults = [p.default_value for p in declaration.parameters]
        elif symbol.declaration is None and func_name in BUILTIN_DEFAULTS:
            defaults = builtin_defaults(func_name, expected_count)
        else:
            defaults = []
        required_count = sum(1 for d in defaults if d is None) if defaults else expected_count
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
            if (i == 0 and func_name in INT_OR_TEXT_BUILTINS and symbol.declaration is None
                    and self._is_string_type(actual_type)):
                continue  # toHex("255") - text holding a whole number (Task 18.3.6d)
            if isinstance(expected_type, ArrayType):
                self._check_array_argument(func_name, i, arg, expected_type, actual_type)
            elif not self.types_compatible(expected_type, actual_type):
                self.errors.append(SemanticError(
                    f"Argument {i+1} to '{func_name}': expected {self.type_to_string(expected_type)}, "
                    f"got {self.type_to_string(actual_type)}",
                    arg.location
                ))

        return func_type.return_type

    def _check_print_call(self, node: CallExpr, func_type: FunctionType,
                          name: str = 'print') -> TypeNode:
        """Check print(text, arg1, arg2, ...) (Task 18.2.2b).

        The text's {@N} placeholders refer to the arguments after it, by number from 1 - in
        any order and as often as wanted. Every argument must be printable. An argument that
        no placeholder uses is only a warning: a translated message may leave one out.

        Returns:
            print's return type (void)
        """
        text, extras = node.arguments[0], node.arguments[1:]

        # {@N} placeholders only mean something in print's or format's own text
        if isinstance(text, InterpolatedStringExpr):
            self.placeholder_texts.add(id(text))
        text_type = self.visit(text)
        string_type = func_type.parameter_types[0]
        if not self.types_compatible(string_type, text_type):
            self.errors.append(SemanticError(
                f"Argument 1 to '{name}': expected {self.type_to_string(string_type)}, got "
                f"{self.type_to_string(text_type)}",
                text.location
            ))

        positions = []
        if isinstance(text, InterpolatedStringExpr):
            positions = [s.index for s in text.segments if isinstance(s, StringPositionalPart)]

        if extras and not positions:
            self.errors.append(SemanticError(
                f"{name}() was given {len(extras)} argument(s) after its text, but the text has "
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
                    f"{{@{index}}} has no matching argument - {name}() was given {len(extras)} "
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
                    f"Argument {number + 1} to {name}() isn't used - no {{@{number}}} placeholder "
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
                elif isinstance(body_type, ArrayType):
                    self.errors.append(SemanticError(
                        "A lambda can't return an array yet - use a named function",
                        node.location
                    ))
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
        # "x is {x}" is an ordinary string value anywhere since Task 18.3.3 (it used to work
        # only inside print - Task 15.10). {@N} placeholders still need print/format, which
        # supply the arguments they refer to
        if id(node) not in self.placeholder_texts and any(
                isinstance(s, StringPositionalPart) for s in node.segments):
            self.errors.append(SemanticError(
                "{@1}-style placeholders only work in the text given to print(...) or "
                "format(...) - they refer to the arguments that follow it",
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
        self._allow_array_call(node.array)  # make()[0] (Task 18.2.4)
        array_type = self.visit(node.array)
        index_type = self.visit(node.index)

        # s[i] reads one character of a string - bounds-checked at run time (18.3.2)
        if self._is_string_type(array_type):
            if not (isinstance(index_type, PrimitiveType) and index_type.name == 'int'):
                self.errors.append(SemanticError(
                    f"String index must be int, got {self.type_to_string(index_type)}",
                    node.index.location))
            return PrimitiveType(location=node.location, name='char')

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
        self._allow_array_call(node.expression)  # calling make() and ignoring the result
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

        self._allow_array_call(node.initializer)  # int[3] a = make() (Task 18.2.4)
        init_type = self.visit(node.initializer)
        if not isinstance(init_type, ArrayType):
            self.errors.append(SemanticError(
                f"Cannot initialize array '{node.name}' with non-array value of type "
                f"{self.type_to_string(init_type)}",
                node.location
            ))
            return

        # An array returned by a function is copied in (Task 18.2.4)
        if isinstance(node.initializer, CallExpr):
            if node.is_const:
                self.errors.append(SemanticError(
                    f"const array '{node.name}' must be initialized with an array literal - "
                    f"copying a returned array into a const array isn't supported yet",
                    node.location
                ))
            if array_type.size is None:
                array_type.size = init_type.size
            self._check_array_copy(f"array '{node.name}'", array_type, init_type, node.location)
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
            # A whole array can be replaced by one a function returns (Task 18.2.4) - copied
            # element by element. From another array variable it still isn't supported
            if isinstance(node.value, CallExpr):
                if symbol.is_constant:
                    self.errors.append(SemanticError(
                        f"Cannot assign to constant: '{target_name}'", node.location))
                self._allow_array_call(node.value)
                value_type = self.visit(node.value)
                self._check_array_copy(f"array '{target_name}'", symbol.data_type, value_type,
                                       node.location)
                return
            self.errors.append(SemanticError(
                f"Cannot reassign array '{target_name}' as a whole - assign to individual "
                f"elements instead (e.g. {target_name}[i] = value), or assign the array a "
                f"function returns ({target_name} = make())",
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

        if self._is_string_type(getattr(target.array, 'inferred_type', None)):
            self.errors.append(SemanticError(
                "A string can't be changed in place yet (Task 17) - build a new string "
                "instead, e.g. with substring() and +",
                node.location))
            self.visit(node.value)
            return

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
            if isinstance(node.value, CallExpr):
                # Replaced by an array a function returns (Task 18.2.4)
                root = self._root_variable(target.object)
                symbol = self.symbol_table.lookup(root.name) if root is not None else None
                if root is None:
                    self.errors.append(SemanticError(
                        f"Can only assign to field '{target.member}' of a struct stored in a "
                        f"variable", node.location))
                elif symbol and symbol.is_constant:
                    self.errors.append(SemanticError(
                        f"Cannot assign to field '{target.member}' of constant '{root.name}'",
                        node.location))
                self._allow_array_call(node.value)
                value_type = self.visit(node.value)
                self._check_array_copy(f"field '{target.member}'", field_type, value_type,
                                       node.location)
                return
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

    def _check_array_copy(self, target: str, expected: ArrayType, actual: TypeNode,
                          location) -> bool:
        """Check that an array value can be copied into `expected` element by element
        (Task 18.2.4): same element type exactly (the copy is byte-for-byte, so no int ->
        float promotion), and the same, known size.

        Returns:
            True if it can
        """
        if not isinstance(actual, ArrayType):
            self.errors.append(SemanticError(
                f"Cannot copy {self.type_to_string(actual)} into {target} of type "
                f"{self.type_to_string(expected)}", location))
            return False
        if not self.types_equal(expected.element_type, actual.element_type):
            self.errors.append(SemanticError(
                f"Cannot copy {self.type_to_string(actual)} into {target} of type "
                f"{self.type_to_string(expected)} - element types must match exactly",
                location))
            return False
        if actual.size is None:
            self.errors.append(SemanticError(
                f"Cannot copy into {target}: the array's size is only known at run time",
                location))
            return False
        if expected.size != actual.size:
            self.errors.append(SemanticError(
                f"Cannot copy {self.type_to_string(actual)} into {target} of type "
                f"{self.type_to_string(expected)} - the sizes differ", location))
            return False
        return True

    def _check_array_return(self, node: ReturnStmt) -> None:
        """Check `return <value>` in a function returning a fixed-size array (Task 18.2.4).

        The value can be an array literal of exactly the right size (numbers may be
        promoted, as in any array literal), or any array of exactly the same type and size -
        a variable, parameter, struct field, or another call returning one. It's copied.
        """
        expected: ArrayType = self.current_function_return_type
        self._allow_array_call(node.value)
        actual = self.visit(node.value)
        if expected.size is None:
            return  # the unsized return type is already reported by the name resolver
        if isinstance(node.value, ArrayLiteralExpr):
            if len(node.value.elements) != expected.size:
                self.errors.append(SemanticError(
                    f"Returned array has {len(node.value.elements)} element(s), but the "
                    f"function returns {self.type_to_string(expected)}", node.location))
            elif node.value.elements and not self.types_compatible(expected.element_type,
                                                                    actual.element_type):
                self.errors.append(SemanticError(
                    f"Returned array has elements of type "
                    f"{self.type_to_string(actual.element_type)}, but the function returns "
                    f"{self.type_to_string(expected)}", node.location))
            return
        self._check_array_copy("the returned array", expected, actual, node.location)

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

        if node.value and isinstance(self.current_function_return_type, ArrayType):
            self._check_array_return(node)
        elif node.value:
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
