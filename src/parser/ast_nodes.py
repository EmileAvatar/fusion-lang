"""
AST Node Definitions for Fusion Programming Language

This module defines all Abstract Syntax Tree (AST) node classes used to represent
the structure of Fusion programs during parsing and compilation.

All nodes inherit from ASTNode and support the visitor pattern for tree traversal.
"""

from dataclasses import dataclass, field
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
        arguments: List of argument expressions, as written - a named argument
            (`crew = 100`) is a NamedArgument wrapping its value (Task 18.2.2)
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
        resolved_arguments: One value expression per parameter, in parameter order: the
            arguments as written (named ones moved to their parameter's position) plus the
            default value of every omitted parameter - set by the type checker (Tasks
            18.1.1, 18.2.2). None until type-checked; codegen uses it when set, since C has
            no defaults or named arguments
        callee_declaration: For a direct call to a declared function, its FunctionDecl; for
            a struct constructor such as Point(3, 4), the StructDecl (Task 18.2.1) - set by
            the type checker; None for builtins and calls through function values
    """
    callee: ASTNode  # Usually IdentifierExpr
    arguments: List[ASTNode]
    inferred_type: Optional['TypeNode'] = None
    resolved_arguments: Optional[List[ASTNode]] = None
    callee_declaration: Optional[Any] = None


@dataclass
class NamedArgument(ASTNode):
    """A named argument in a call: `crew = 100` in createShip(crew = 100) (Task 18.2.2)

    Only valid as an element of CallExpr.arguments. Works for declared functions and struct
    constructors; not for builtins or calls through function values (a function type has no
    parameter names).

    Attributes:
        name: The parameter (or struct field) name
        value: The argument's value expression
    """
    name: str
    value: ASTNode


@dataclass
class LambdaExpr(ASTNode):
    """Lambda expression: (int x, int y) : x + y, or func(int x) : x * 2

    Inline lambda with colon syntax for single-expression functions.

    Attributes:
        parameters: List of parameter declarations
        return_type: Return type node - not written in the source, so the parser leaves it
            None and the type checker infers it from the body (Task 18.1.3)
        body: Lambda body (single expression or BlockStmt for multi-line)
        inferred_type: Type resolved by the semantic analyzer (None until type-checked)
        scope: The lambda's parameter scope, set by the name resolver so the type checker
            can re-enter it (same pattern as BlockStmt.scope)
    """
    parameters: List['ParameterDecl']
    return_type: Optional['TypeNode']
    body: ASTNode  # Single expression or BlockStmt
    inferred_type: Optional['TypeNode'] = None
    scope: Optional[Any] = None


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
class MemberExpr(ASTNode):
    """Struct field access: point.x (Task 18.2.1)

    Attributes:
        object: The expression whose field is read (a struct value)
        member: The field name
        inferred_type: Type resolved by the semantic analyzer (the field's type, None until
            type-checked)
    """
    object: ASTNode
    member: str
    inferred_type: Optional['TypeNode'] = None


@dataclass
class EnumValueExpr(ASTNode):
    """One value of an enum: Color.Red (Task 25.2). The parser reads it as a MemberExpr;
    src/semantic/enums.py turns it into this node once it knows Color is an enum.

    Attributes:
        enum_name: The enum's (internal) name, e.g. "Color" or "paint.Color"
        member: The value's name, e.g. "Red"
        declaration: The EnumDecl (set when the node is made)
    """
    enum_name: str
    member: str
    declaration: Optional[Any] = None
    inferred_type: Optional['TypeNode'] = None


@dataclass
class EnumStaticCall(ASTNode):
    """A call on the enum itself: Color.values(), Color.fromString("Red") (Task 25.2), or
    a value with data, Token.Number(42) (Task 25.4) - made from a CallExpr by
    src/semantic/enums.py.

    Attributes:
        enum_name: The enum's (internal) name
        method: "values" or "fromString"
        arguments: The call's arguments
        declaration: The EnumDecl
    """
    enum_name: str
    method: str
    arguments: List[ASTNode]
    declaration: Optional[Any] = None
    inferred_type: Optional['TypeNode'] = None
    resolved_arguments: Optional[List[ASTNode]] = None   # Token.Number(...): one per field


@dataclass
class ErrorMakeExpr(ASTNode):
    """Error("No such file", 404) / FileError("Can't open", path = "x") - an error value
    (Task 26, 26.9). The parser reads it as a call; src/semantic/error_rules.py turns it
    into this node.

    Attributes:
        arguments: message, code, then the type's fields - by position or by name
        declaration: The ErrorDecl of a custom error type (None for Error)
        resolved_arguments: one value per slot (message, code, fields...), after checking
    """
    arguments: List[ASTNode]
    inferred_type: Optional['TypeNode'] = None
    declaration: Optional[Any] = None
    resolved_arguments: Optional[List[ASTNode]] = None


@dataclass
class ErrorActiveExpr(ASTNode):
    """`if err` - true when an Error value holds an error (Task 26); made by the type checker
    where an Error is used as a condition."""
    operand: ASTNode
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
class StringPositionalPart:
    """A positional placeholder within an interpolated string: {@1}, {@2}, ... (Task 18.2.2b)

    Refers to print's extra arguments by number, starting at 1 - in any order, and as often
    as wanted: print("{@2} before {@1}", a, b).

    Attributes:
        index: The placeholder number (1 = the first argument after the text)
    """
    index: int


@dataclass
class InterpolatedStringExpr(ASTNode):
    """Interpolated string expression: "Hello {name}, you are {age} years old"

    Supports two interpolation syntaxes:
    - Inline: {variable} or a struct field path {point.x} (StringExprPart)
    - Positional: {@1}, {@2}, ... (StringPositionalPart) - print's extra arguments

    Represented as a single ordered list of text/expression segments (rather than two
    parallel arrays) so the structure cannot desync between text and interpolated
    expressions - see taskSummary2.md Task 12.4.

    Attributes:
        segments: Ordered list of StringTextPart, StringExprPart and StringPositionalPart
            segments
        inferred_type: Type resolved by the semantic analyzer (always string once resolved)
    """
    segments: List[Union[StringTextPart, StringExprPart, 'StringPositionalPart']]
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
    # `Ship s, Error err = loadShip(f)` - the variable that captures an error (Task 26)
    error_name: Optional[str] = None
    error_location: Optional[Any] = None
    error_type: Optional['TypeNode'] = None   # `Ship s, FileError err` (26.10); None: Error


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
class CatchClause(ASTNode):
    """`catch FileError e` / `catch e` / `catch` (Tasks 26.3, 26.11).

    Attributes:
        error_type: The error type it catches (None: any error)
        name: The variable that gets the error (None for a bare `catch`)
        body: The catch block
    """
    error_type: Optional['TypeNode'] = None
    name: Optional[str] = None
    body: Optional['BlockStmt'] = None


@dataclass
class TryStmt(ASTNode):
    """try / catch ... / finally (Tasks 26.3, 26.11). An error in the body goes to the first
    catch whose type matches (a parent type catches its subtypes; an untyped catch any
    error); one no catch matches goes on. `finally` always runs - after the body, after a
    catch, when an error passes through, and before a return / break / continue leaves the
    try.

    Attributes:
        body: The try block
        catches: The catch clauses, in order
        finally_body: The finally block, or None
    """
    body: 'BlockStmt'
    catches: List[CatchClause] = field(default_factory=list)
    finally_body: Optional['BlockStmt'] = None


@dataclass
class ThrowStmt(ASTNode):
    """throw Error("...") / throw err (Task 26.3) - start an error on its way."""
    value: ASTNode


@dataclass
class MatchPattern(ASTNode):
    """One thing a `case` matches (Task 25.3): an enum value's bare name (`Red`), with the
    names its data is bound to (`Number(n)`, Task 25.4) - or a constant (`'+'`, `42`, "go").

    Attributes:
        name: The enum value's name, for an enum pattern (None for a constant)
        bindings: The names given to the value's data, in field order (Task 25.4)
        value: The constant - a LiteralExpr, or `-` and a number (None for an enum pattern)
    """
    name: Optional[str] = None
    bindings: List[str] = field(default_factory=list)
    value: Optional[ASTNode] = None
    dotted: bool = False      # `case files.FileError` - an error type from a module (26.10)


@dataclass
class MatchCase(ASTNode):
    """`case A, B` and its body (Task 25.3)."""
    patterns: List[MatchPattern]
    body: 'BlockStmt'


@dataclass
class MatchStmt(ASTNode):
    """match subject / case ... / else ... (Task 25.3). No fall-through: exactly one case
    (or the else) runs. On an enum every value must be covered unless there is an `else`;
    on an int, char or string an `else` is required.

    Attributes:
        subject: The value matched
        cases: The cases, in order
        else_body: The `else` block, or None
    """
    subject: ASTNode
    cases: List[MatchCase]
    else_body: Optional['BlockStmt'] = None


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
        scope: The loop variable's Scope (src.semantic.symbol.Scope), populated by
            NameResolver and reused by TypeChecker - block scoping (Task 12.6) means the
            loop variable itself is scoped to the loop, not the whole function. Typed as
            Any rather than importing Scope, which would create a circular import
            (symbol.py already imports from this module).
    """
    variable: str
    iterable: ASTNode
    body: ASTNode
    scope: Any = None


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
        scope: This block's Scope (src.semantic.symbol.Scope), populated by NameResolver
            and reused by TypeChecker so both passes see the same block-scoped symbols
            (Task 12.6 - block-level/lexical scoping). None until NameResolver runs; code
            that constructs a BlockStmt directly without running NameResolver first (some
            unit tests do) gets function/isolated-scope behavior as a fallback - see
            TypeChecker.visit_BlockStmt. Typed as Any rather than importing Scope, which
            would create a circular import (symbol.py already imports from this module).
    """
    statements: List[ASTNode]
    scope: Any = None


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
    is_variadic: bool = False   # `string... args` - main's arguments (Task 18.5.4)


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
    is_public: bool = False  # `public` - other modules may use it (Task 18.4.3)
    returns_error: bool = False  # `Ship, Error function` / `Error function` - can fail (Task 26)


@dataclass
class StructField(ASTNode):
    """One field of a struct declaration: int x, or int hp = 100 (Task 18.2.1)

    Attributes:
        field_type: The field's type node
        name: Field name
        default_value: Optional constant default (same rule as parameter defaults)
    """
    field_type: 'TypeNode'
    name: str
    default_value: Optional[ASTNode] = None


@dataclass
class StructDecl(ASTNode):
    """Struct declaration (Task 18.2.1): a pure value type - fields only, no methods.

    The compiler generates the only constructor, Point(3, 4), with arguments in field order.

    Attributes:
        name: Struct name, which is also the type name
        fields: The fields, in declaration order
    """
    name: str
    fields: List[StructField]
    is_public: bool = False  # `public` - other modules may use it (Task 18.4.3)


@dataclass
class ErrorDecl(ASTNode):
    """A custom error type (Task 26.9, user decisions 2026-10-16):

        error FileError                     error FileNotFound : FileError
            string path                         message = "File not found"
            int attempts = 1                    bool wasDeleted

    Every error type is an Error: it has message, code and where, plus its parent's fields
    and its own.

    Attributes:
        name: The type's name
        parent: The parent error type's name ("Error" when none is written)
        fields: Its own fields (not the parent's)
        default_message: `message = "..."` - used when none is given (None: required)
        default_code: `code = ...` - used when none is given (None: 0)
    """
    name: str
    parent: str = 'Error'
    fields: List['StructField'] = field(default_factory=list)
    default_message: Optional[ASTNode] = None
    default_code: Optional[ASTNode] = None
    is_public: bool = False  # `public` - other modules may use it (Task 18.4.3)
    parent_declaration: Optional[Any] = None   # set by the name resolver
    builtin: bool = False    # one of Fusion's own error types (Task 26.12)


@dataclass
class EnumVariant(ASTNode):
    """One value of an enum (Task 25): `Red`, `OK = 200`, or with data `Number(int value)`.

    Attributes:
        name: The value's name
        value: Its integer value - written (`= 200`), or the previous one + 1 (from 0);
            filled in by the parser
        explicit_value: True when the source wrote `= n`
        fields: The data it carries (Task 25.4) - empty for a plain value
    """
    name: str
    value: int = 0
    explicit_value: bool = False
    fields: List[StructField] = field(default_factory=list)


@dataclass
class EnumDecl(ASTNode):
    """An enum declaration (Task 25), in any block style or on one line:

        enum Color: Red Green Blue          enum Status
                                                OK = 200
                                                NotFound = 404

    Attributes:
        name: The enum's name, which is also the type name
        variants: Its values, in declaration order
    """
    name: str
    variants: List[EnumVariant]
    is_public: bool = False  # `public` - other modules may use it (Task 18.4.3)

    def variant(self, name: str) -> Optional[EnumVariant]:
        return next((v for v in self.variants if v.name == name), None)


@dataclass
class ProgramNode(ASTNode):
    """Root node of the AST representing the entire program.

    Attributes:
        declarations: List of top-level declarations (functions, structs, etc.)
        imports: The file's `import` lines (Task 18.4.2) - resolved by src/modules/loader.py
    """
    declarations: List[ASTNode]  # FunctionDecl, StructDecl, etc.
    imports: List['ImportDecl'] = field(default_factory=list)


@dataclass
class ImportDecl(ASTNode):
    """An import line (Task 18.4.2): `import money`, `import money.Price`,
    `import money.*`, `import lib.utils as libutils`.

    Attributes:
        path: The dotted path, without a trailing `*` (["money", "Price"])
        star: True for `import money.*`
        alias: The name given with `as`, or None
    """
    path: List[str]
    star: bool = False
    alias: Optional[str] = None


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


@dataclass
class ListType(TypeNode):
    """A growable list: List<int> (Task 18.5.1) - a value; copies are independent."""
    element_type: TypeNode


@dataclass
class MapType(TypeNode):
    """A key -> value map: Map<string, int>, also written Dictionary<...> (Task 18.5.2)."""
    key_type: TypeNode
    value_type: TypeNode


# Built-in generic collection types, by the name used in source (Task 18.5)
COLLECTION_TYPE_NAMES = ('List', 'Map', 'Dictionary')


@dataclass
class NewCollectionExpr(ASTNode):
    """An empty collection: List<int>(), Map<string, int>() (Task 18.5)."""
    collection_type: TypeNode
    inferred_type: Optional['TypeNode'] = None


@dataclass
class StructType(TypeNode):
    """A struct used as a type: Point p (Task 18.2.1)

    The parser only knows the name - a plain identifier in a type position. The name
    resolver checks that a struct of that name exists and links its declaration here.

    Attributes:
        name: The struct's name
        declaration: The StructDecl, set by the name resolver (None until then)
    """
    name: str
    declaration: Optional[Any] = None


@dataclass
class ErrorType(TypeNode):
    """The built-in Error type (Task 26): message, code, where - or a custom error type
    (26.9), whose ErrorDecl is in `declaration`. The parser reads an error type's name as a
    struct name; src/semantic/error_rules.py replaces it with this."""
    name: str = 'Error'
    declaration: Optional[Any] = None   # the ErrorDecl of a custom error type


@dataclass
class EnumType(TypeNode):
    """An enum used as a type: Color c (Task 25.2). The parser can't tell an enum name from
    a struct name, so it makes a StructType; src/semantic/enums.py replaces it with this.

    Attributes:
        name: The enum's (internal) name
        declaration: The EnumDecl
    """
    name: str
    declaration: Optional[Any] = None
