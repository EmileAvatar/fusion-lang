"""
AST Node Definitions for Fusion Programming Language

This module defines all Abstract Syntax Tree (AST) node classes used to represent
the structure of Fusion programs during parsing and compilation.

All nodes inherit from ASTNode and support the visitor pattern for tree traversal.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Union
from src.lexer.token import SourceLocation


# ============================================================================
# Base AST Node
# ============================================================================

@dataclass
class ASTNode:
    """Base class for all AST nodes.

    All AST nodes track their source location for error reporting and support
    the visitor pattern for tree traversal.

    Attributes:
        location: Source location (file, line, column) for error reporting
    """
    location: SourceLocation

    def accept(self, visitor):
        """Accept a visitor for tree traversal (visitor pattern).

        Args:
            visitor: Object implementing visit_* methods for each node type

        Returns:
            Result from the visitor's visit method

        Raises:
            NotImplementedError: If visitor doesn't implement the required method
        """
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, None)
        if method:
            return method(self)
        raise NotImplementedError(f"Visitor does not implement {method_name}")


# ============================================================================
# Expression Nodes
# ============================================================================

@dataclass
class LiteralExpr(ASTNode):
    """Literal expression: 42, 3.14, "hello", 'c', true, false, null

    Attributes:
        value: The literal value (int, float, str, bool, None)
        type_hint: String indicating the type ("int", "float", "string", "char", "bool", "null")
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
    """
    value: Any  # int, float, str, bool, None
    type_hint: str  # "int", "float", "string", "char", "bool", "null"
    inferred_type: Optional['TypeNode'] = None


@dataclass
class IdentifierExpr(ASTNode):
    """Identifier expression: variable_name, function_name

    Attributes:
        name: The identifier name
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
    """
    name: str
    inferred_type: Optional['TypeNode'] = None


@dataclass
class BinaryExpr(ASTNode):
    """Binary expression: left op right

    Examples: a + b, x == y, i < 10

    Attributes:
        left: Left operand expression
        operator: Binary operator string ("+", "-", "*", "/", "==", "!=", "<", ">", etc.)
        right: Right operand expression
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
    """
    left: ASTNode
    operator: str  # "+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">=", "and", "or", etc.
    right: ASTNode
    inferred_type: Optional['TypeNode'] = None


@dataclass
class UnaryExpr(ASTNode):
    """Unary expression: op operand

    Examples: -x, not y, !flag

    Attributes:
        operator: Unary operator string ("-", "not", "!")
        operand: The operand expression
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
    """
    operator: str  # "-", "not", "!"
    operand: ASTNode
    inferred_type: Optional['TypeNode'] = None


@dataclass
class CallExpr(ASTNode):
    """Function call expression: func(arg1, arg2, ...)

    Examples: print("hello"), add(5, 3), max(a, b, c)

    Attributes:
        callee: The function expression (usually IdentifierExpr)
        arguments: List of argument expressions
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
    """
    callee: ASTNode  # Usually IdentifierExpr
    arguments: List[ASTNode]
    inferred_type: Optional['TypeNode'] = None


@dataclass
class LambdaExpr(ASTNode):
    """Lambda expression: (int x, int y) : x + y

    Inline lambda with colon syntax for single-expression functions.

    Attributes:
        parameters: List of parameter declarations
        return_type: Return type node
        body: Lambda body (single expression or BlockStmt for multi-line)
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
    """
    parameters: List['ParameterDecl']
    return_type: 'TypeNode'
    body: ASTNode  # Single expression or BlockStmt
    inferred_type: Optional['TypeNode'] = None


@dataclass
class ArrayLiteralExpr(ASTNode):
    """Array literal expression: [1, 2, 3]

    Attributes:
        elements: List of element expressions
        inferred_type: Type resolved by the semantic analyzer (an ArrayType, None until
            type-checked)
    """
    elements: List[ASTNode]
    inferred_type: Optional['TypeNode'] = None


@dataclass
class IndexExpr(ASTNode):
    """Array index expression: arr[index]

    Attributes:
        array: The array expression being indexed
        index: The index expression (must resolve to int)
        inferred_type: Type resolved by the semantic analyzer (the array's element type,
            None until type-checked)
    """
    array: ASTNode
    index: ASTNode
    inferred_type: Optional['TypeNode'] = None


@dataclass
class StringTextPart:
    """A literal text segment within an interpolated string.

    Attributes:
        text: The literal text content
    """
    text: str


@dataclass
class StringExprPart:
    """An interpolated expression segment within an interpolated string.

    Attributes:
        expression: The expression node to evaluate and interpolate
    """
    expression: ASTNode


@dataclass
class InterpolatedStringExpr(ASTNode):
    """Interpolated string expression: "Hello {name}, you are {age} years old"

    Supports two interpolation syntaxes:
    - Inline: {variable_name}
    - Positional: {@1}, {@2}, ...

    Represented as a single ordered list of text/expression segments (rather than two
    parallel arrays) so the structure cannot desync between text and interpolated
    expressions - see taskSummary2.md Task 12.4.

    Attributes:
        segments: Ordered list of StringTextPart and StringExprPart segments
        inferred_type: Type resolved by the semantic analyzer (always string once resolved)
    """
    segments: List[Union[StringTextPart, StringExprPart]]
    inferred_type: Optional['TypeNode'] = None


# ============================================================================
# Statement Nodes
# ============================================================================

@dataclass
class ExpressionStmt(ASTNode):
    """Expression as statement: print(x), func()

    Attributes:
        expression: The expression to execute
    """
    expression: ASTNode


@dataclass
class VarDeclStmt(ASTNode):
    """Variable declaration: int x = 5, const int y = 10

    Attributes:
        var_type: Type node for the variable
        name: Variable name
        initializer: Initial value expression (optional for var, required for const)
        is_const: True if declared with const keyword, False otherwise
    """
    var_type: 'TypeNode'
    name: str
    initializer: Optional[ASTNode]
    is_const: bool = False


@dataclass
class AssignmentStmt(ASTNode):
    """Assignment statement: x = value

    Attributes:
        target: Target expression (usually IdentifierExpr)
        value: Value expression to assign
    """
    target: ASTNode  # Usually IdentifierExpr
    value: ASTNode


@dataclass
class IfStmt(ASTNode):
    """If statement: if condition { body } else { else_body }

    Attributes:
        condition: Boolean condition expression
        then_branch: Statement to execute if true (usually BlockStmt)
        else_branch: Optional else statement (BlockStmt or another IfStmt for else-if)
    """
    condition: ASTNode
    then_branch: ASTNode  # Usually BlockStmt
    else_branch: Optional[ASTNode]  # BlockStmt or another IfStmt


@dataclass
class WhileStmt(ASTNode):
    """While loop: while condition { body }

    Attributes:
        condition: Loop condition expression
        body: Loop body statement (usually BlockStmt)
    """
    condition: ASTNode
    body: ASTNode


@dataclass
class ForStmt(ASTNode):
    """For loop: for variable in iterable { body }

    Attributes:
        variable: Loop variable name
        iterable: Iterable expression (range, list, etc.)
        body: Loop body statement (usually BlockStmt)
    """
    variable: str
    iterable: ASTNode
    body: ASTNode


@dataclass
class ReturnStmt(ASTNode):
    """Return statement: return value

    Attributes:
        value: Value expression to return (None for void returns)
    """
    value: Optional[ASTNode]


@dataclass
class BreakStmt(ASTNode):
    """Break statement: break

    Exits the innermost loop immediately.
    """
    pass


@dataclass
class ContinueStmt(ASTNode):
    """Continue statement: continue

    Skips to the next iteration of the innermost loop.
    """
    pass


@dataclass
class BlockStmt(ASTNode):
    """Block statement: { stmt1; stmt2; ... }

    Represents a sequence of statements enclosed in braces or indentation.

    Attributes:
        statements: List of statements in the block
    """
    statements: List[ASTNode]


# ============================================================================
# Declaration Nodes
# ============================================================================

@dataclass
class ParameterDecl(ASTNode):
    """Function parameter declaration: int x = default_value

    Attributes:
        param_type: Parameter type node
        name: Parameter name
        default_value: Optional default value expression
    """
    param_type: 'TypeNode'
    name: str
    default_value: Optional[ASTNode]


@dataclass
class FunctionDecl(ASTNode):
    """Function declaration: int function add(int a, int b) { return a + b }

    Supports both regular functions and inline lambdas.

    Attributes:
        return_type: Return type node
        name: Function name
        parameters: List of parameter declarations
        body: Function body (BlockStmt or single expression for lambdas)
        is_lambda: True for inline lambdas with ":" syntax
    """
    return_type: 'TypeNode'
    name: str
    parameters: List[ParameterDecl]
    body: ASTNode  # BlockStmt or single expression (for lambdas)
    is_lambda: bool = False  # True for inline lambdas with ":"


@dataclass
class ProgramNode(ASTNode):
    """Root node of the AST representing the entire program.

    Attributes:
        declarations: List of top-level declarations (functions, variables, etc.)
    """
    declarations: List[ASTNode]  # FunctionDecl, VarDeclStmt, etc.


# ============================================================================
# Type Nodes
# ============================================================================

@dataclass
class TypeNode(ASTNode):
    """Base class for type nodes.

    Type nodes represent type information in the AST (variable types,
    function return types, parameter types, etc.)
    """
    pass


@dataclass
class PrimitiveType(TypeNode):
    """Primitive type: int, float, string, bool, char, void

    Attributes:
        name: Type name ("int", "float", "string", "bool", "char", "void")
    """
    name: str  # "int", "float", "string", "bool", "char", "void"


@dataclass
class FunctionType(TypeNode):
    """Function type (for lambdas and function pointers): (int, int) -> int

    Attributes:
        parameter_types: List of parameter type nodes
        return_type: Return type node
    """
    parameter_types: List[TypeNode]
    return_type: TypeNode


@dataclass
class ArrayType(TypeNode):
    """Array type: int[], int[5], float[10]

    Fixed-size only (Task 9 v1) - size is either given explicitly (`int[5]`) or left
    unresolved (`int[]`, size=None) until the semantic analyzer infers it from an array
    literal initializer. Not nullable, not a function parameter/return type yet - see
    taskSummary2.md Task 9 for the deferred nullable-array design.

    Attributes:
        element_type: Type of each array element
        size: Number of elements, or None until resolved by the semantic analyzer
    """
    element_type: TypeNode
    size: Optional[int] = None
