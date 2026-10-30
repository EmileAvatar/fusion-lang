"""
Recursive Descent Parser for Fusion Programming Language

This module implements a parser that converts a token stream into an Abstract
Syntax Tree (AST). Uses precedence climbing for binary operators.
"""

import copy
import json
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import List, Optional
from src.lexer.token import Token, TokenType, SourceLocation
from src.lexer.literals import decode_char_literal, integer_value
from src.parser.ast_nodes import *

# `byVal a` / `byValue a` - a copy; `byRef a` - shared (Task 32.10a; words, not keywords)
PASSING_WORDS = {'byVal': True, 'byValue': True, 'byRef': False}


class ParserError(Exception):
    """Exception raised for parser errors.

    Attributes:
        token: The token where the error occurred
        message: Error description
    """

    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(f"{message} at {token.location}")


class Parser:
    """Recursive descent parser for Fusion language.

    Converts a stream of tokens into an Abstract Syntax Tree (AST).
    Uses precedence climbing for binary operator parsing.

    Attributes:
        tokens: List of tokens to parse
        current: Current position in token list
    """

    def __init__(self, tokens: List[Token]):
        """Initialize parser with token list.

        Args:
            tokens: List of tokens from lexer (must include EOF token)
        """
        self.tokens = tokens
        self.current = 0
        # Inside an if / while / else-if condition `=` compares, like `==` (Task 18.3.5)
        self.in_condition = False

    # ========================================================================
    # Token Navigation
    # ========================================================================

    def is_at_end(self) -> bool:
        """Check if we've reached EOF token.

        Returns:
            True if current token is EOF
        """
        return self.peek().type == TokenType.EOF

    def peek(self, offset: int = 0) -> Token:
        """Look ahead at token without consuming.

        Args:
            offset: How many tokens ahead to look (default 0 = current)

        Returns:
            Token at current + offset position
        """
        index = self.current + offset
        if index >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[index]

    def advance(self) -> Token:
        """Consume and return current token.

        Returns:
            The token that was just consumed
        """
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        """Return previously consumed token.

        Returns:
            The token at current - 1
        """
        return self.tokens[self.current - 1]

    def check(self, token_type: TokenType) -> bool:
        """Check if current token matches type without consuming.

        Args:
            token_type: TokenType to check against

        Returns:
            True if current token matches type
        """
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the types and consume if so.

        Args:
            token_types: Variable number of TokenTypes to check

        Returns:
            True if matched and consumed, False otherwise
        """
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error.

        Args:
            token_type: Expected TokenType
            message: Error message if token doesn't match

        Returns:
            The consumed token

        Raises:
            ParserError: If current token doesn't match expected type
        """
        if self.check(token_type):
            return self.advance()
        raise ParserError(self.peek(), message)

    # ========================================================================
    # Expression Parsing (Precedence Climbing)
    # ========================================================================

    def parse_expression(self) -> ASTNode:
        """Parse any expression (entry point for expressions).

        Starts at lowest precedence (logical OR) and climbs up.

        Returns:
            Expression AST node
        """
        return self.parse_conditional()

    def parse_conditional(self) -> ASTNode:
        """The conditional operator (Task 30.7): `condition ? a : b`, usually written with the
        condition in brackets - `(count > 5) ? "big" : "small"`. Lowest precedence; nests to
        the right: `a ? b : c ? d : e` is `a ? b : (c ? d : e)`."""
        condition = self.parse_or()
        if not self.check(TokenType.QUESTION):
            return condition
        question = self.advance()
        then_value = self.parse_conditional()
        self.consume(TokenType.COLON, "Expected ':' between the two values of '? :' - "
                                      "(condition) ? a : b")
        else_value = self.parse_conditional()
        return ConditionalExpr(location=question.location, condition=condition,
                               then_value=then_value, else_value=else_value)

    def parse_or(self) -> ASTNode:
        """Parse logical OR: expr or expr, expr || expr

        Precedence: 8 (lowest)
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_and()

        while self.match(TokenType.OR, TokenType.LOGICAL_OR):
            operator = self.previous().value
            right = self.parse_and()
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        return expr

    def parse_and(self) -> ASTNode:
        """Parse logical AND: expr and expr, expr && expr

        Precedence: 7
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_equality()

        while self.match(TokenType.AND, TokenType.LOGICAL_AND):
            operator = self.previous().value
            right = self.parse_equality()
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        return expr

    def parse_condition(self) -> ASTNode:
        """Parse the condition of an if / while / else if, where `=` compares like `==`
        (Task 18.3.5 - `if x = 2`). Outside a condition `=` is always assignment."""
        outer = self.in_condition
        self.in_condition = True
        try:
            return self.parse_expression()
        finally:
            self.in_condition = outer

    def parse_equality(self) -> ASTNode:
        """Parse equality: expr == expr, expr != expr, expr === expr, expr !== expr,
        and expr = expr inside a condition (Task 18.3.5)

        Precedence: 6
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_relational()

        operators = [TokenType.EQUAL, TokenType.NOT_EQUAL,
                     TokenType.STRICT_EQUAL, TokenType.STRICT_NOT_EQUAL]
        if self.in_condition:
            operators.append(TokenType.ASSIGN)
        while self.match(*operators):
            operator = self.previous().value
            if operator == '=':
                operator = '=='  # `if x = 2` compares by value, the same as `==`
            right = self.parse_relational()
            if self.is_null_literal(right) or self.is_null_literal(expr):
                # x == null / x != null (also ===, !==): a null test (Task 30.11)
                tested = expr if self.is_null_literal(right) else right
                expr = IsNullExpr(location=expr.location, operand=tested,
                                  negated=operator in ('!=', '!=='))
                continue
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        # x is null / x is not null (Task 30.11) - `is` with a type comes later
        if self.check(TokenType.IS):
            self.advance()
            negated = self.match(TokenType.NOT)
            self.consume(TokenType.NULL, "Only 'is null' and 'is not null' exist so far")
            expr = IsNullExpr(location=expr.location, operand=expr, negated=negated)

        return expr

    @staticmethod
    def is_null_literal(node) -> bool:
        return isinstance(node, LiteralExpr) and node.type_hint == 'null'

    def parse_relational(self) -> ASTNode:
        """Parse relational: expr < expr, expr > expr, expr <= expr, expr >= expr

        Precedence: 5
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_additive()

        while self.match(TokenType.LESS, TokenType.GREATER,
                          TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.previous().value
            right = self.parse_additive()
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        return expr

    def parse_additive(self) -> ASTNode:
        """Parse addition/subtraction: expr + expr, expr - expr

        Precedence: 4
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.parse_multiplicative()
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        return expr

    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication/division/modulo: expr * expr, expr / expr, expr % expr

        Precedence: 3
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_unary()

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.previous().value
            right = self.parse_unary()
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        return expr

    def parse_unary(self) -> ASTNode:
        """Parse unary expressions: -expr, not expr, !expr

        Precedence: 2
        Associativity: Right (handled via recursion)

        Returns:
            Expression AST node
        """
        if self.match(TokenType.MINUS, TokenType.NOT, TokenType.LOGICAL_NOT):
            operator_token = self.previous()
            operator = operator_token.value
            operand = self.parse_unary()  # Right associative via recursion
            return UnaryExpr(
                location=operator_token.location,
                operator=operator,
                operand=operand
            )

        # `byVal a` (or byValue) - a copy; `byRef a` - shared (Task 32.10a). Words only here
        passing = self._passing_word()
        if passing is not None:
            word = self.advance()
            return PassingExpr(location=word.location, value=self.parse_unary(),
                               by_val=passing)

        return self.parse_call()

    def _passing_word(self):
        """True for `byVal` / `byValue`, False for `byRef`, before a value or a type; None
        when the word is just a name."""
        if not self.check(TokenType.IDENTIFIER) or self.peek().value not in PASSING_WORDS:
            return None
        if self.peek(1).type not in (TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LBRACKET,
                                     TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                                     TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
                                     TokenType.BYTE):
            return None
        return PASSING_WORDS[self.peek().value]

    def parse_call(self) -> ASTNode:
        """Parse postfix operators: function calls func(...), array indexing arr[...], and
        struct field access point.x (Task 18.2.1)

        Precedence: 1 (postfix operator)

        Returns:
            Expression AST node (CallExpr, IndexExpr, MemberExpr, or primary expression)
        """
        expr = self.parse_primary()

        # Handle chained postfix operators: func()(), arr[i][j], arr[i](), etc.
        while True:
            if self.check(TokenType.SAFE_NAV):
                # x?.null - quick typing for "x is null" (Task 30.11); other x?.member: 30.2
                if self.peek(1).type != TokenType.NULL:
                    raise ParserError(self.peek(), "'?.' before a member or method is planned "
                                                   "(Task 30.2) - today only x?.null works")
                self.advance(); self.advance()
                expr = IsNullExpr(location=expr.location, operand=expr)
                continue
            if self.match(TokenType.LPAREN):
                arguments = []

                # Parse argument list
                if not self.check(TokenType.RPAREN):
                    arguments.append(self.parse_argument())
                    while self.match(TokenType.COMMA):
                        arguments.append(self.parse_argument())

                self.consume(TokenType.RPAREN, "Expected ')' after function arguments")

                expr = CallExpr(
                    location=expr.location,
                    callee=expr,
                    arguments=arguments
                )
            elif self.match(TokenType.LBRACKET):
                index = self.parse_expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after array index")

                expr = IndexExpr(
                    location=expr.location,
                    array=expr,
                    index=index
                )
            elif self.match(TokenType.DOT):
                # Any word may follow '.', a keyword too - m.get(k), x.set(...) (Task 18.5.2):
                # after a dot it can only be a field or method name
                if self.peek().type != TokenType.IDENTIFIER and str(self.peek().value).isidentifier():
                    member = self.advance()
                else:
                    member = self.consume(TokenType.IDENTIFIER, "Expected field name after '.'")
                expr = MemberExpr(
                    location=expr.location,
                    object=expr,
                    member=member.value
                )
            else:
                break

        return expr

    def parse_argument(self) -> ASTNode:
        """Parse one call argument: an expression, or a named argument `name = value`
        (Task 18.2.2).

        Assignment is a statement in Fusion, never an expression, so `name =` at the start of
        an argument can only be a named argument.

        Returns:
            Expression AST node, or NamedArgument
        """
        if self.check(TokenType.IDENTIFIER) and self.peek(1).type == TokenType.ASSIGN:
            name_token = self.advance()
            self.advance()  # =
            return NamedArgument(
                location=name_token.location,
                name=name_token.value,
                value=self.parse_expression()
            )
        return self.parse_expression()

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions: literals, identifiers, parentheses, lambdas.

        Precedence: 1 (highest)

        Returns:
            Expression AST node

        Raises:
            ParserError: If token is not a valid primary expression
        """
        # `new Car("Honda")` - the same as Car("Honda"); `new` only shows an object is made
        # (Task 32.10b)
        if self.match(TokenType.NEW):
            new_token = self.previous()
            made = self.parse_call()
            if not (isinstance(made, CallExpr) and isinstance(made.callee, IdentifierExpr)):
                raise ParserError(new_token, "'new' comes before a class's constructor: new Car(...)")
            made.uses_new = True
            return made

        # A match that gives a value (Task 46.2) - it never falls through
        if self.match(TokenType.MATCH):
            return self.parse_match_value()
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'fall' \
                and self.peek(1).type == TokenType.MATCH:
            raise ParserError(self.peek(), "A match that gives a value can't fall through - "
                                           "'fall match' is a statement")

        # Integer literal
        if self.match(TokenType.INTEGER):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                value=integer_value(token.value),  # 0xFF, 1_000 (Task 18.3.6d)
                type_hint="int"
            )

        # Float literal
        if self.match(TokenType.FLOAT_LIT):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                value=float(token.value),
                type_hint="float"
            )

        # String literal (with interpolation check)
        if self.match(TokenType.STRING_LIT):
            token = self.previous()
            # Lexer returns strings as JSON: [["STRING_PART", "content"]]
            # Parse it to get the actual string value
            try:
                parts = json.loads(token.value)
                if len(parts) == 1 and parts[0][0] == "STRING_PART":
                    # Simple string without interpolation
                    return LiteralExpr(
                        location=token.location,
                        value=parts[0][1],
                        type_hint="string"
                    )
                else:
                    # String with interpolation
                    return self.parse_interpolated_string_from_parts(token, parts)
            except (json.JSONDecodeError, IndexError, KeyError):
                # Fallback: treat as raw string
                return LiteralExpr(
                    location=token.location,
                    value=token.value,
                    type_hint="string"
                )

        # Character literal
        if self.match(TokenType.CHAR_LIT):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                # The token holds the raw text including quotes ("'a'"); the AST holds the
                # decoded character ("a") - see decode_char_literal for why this matters
                value=decode_char_literal(token.value),
                type_hint="char"
            )

        # Boolean literals
        if self.match(TokenType.TRUE):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                value=True,
                type_hint="bool"
            )

        if self.match(TokenType.FALSE):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                value=False,
                type_hint="bool"
            )

        # Null literal
        if self.match(TokenType.NULL):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                value=None,
                type_hint="null"
            )

        # `this` - inside a struct's method, the struct itself (Task 32.1)
        if self.match(TokenType.THIS):
            return IdentifierExpr(location=self.previous().location, name='this')

        # Array literal: [1, 2, 3]
        if self.match(TokenType.LBRACKET):
            start_token = self.previous()
            elements = []

            if not self.check(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    if self.check(TokenType.RBRACKET):
                        break  # Trailing comma
                    elements.append(self.parse_expression())

            self.consume(TokenType.RBRACKET, "Expected ']' after array literal")

            return ArrayLiteralExpr(
                location=start_token.location,
                elements=elements
            )

        # Identifier (allow type keywords and END as identifiers in expression context)
        # This allows calling functions/variables named "double", "string", "end", etc.
        # An empty collection: List<int>(), Map<string, int>() (Task 18.5)
        if self.check(TokenType.IDENTIFIER) and self.peek().value in COLLECTION_TYPE_NAMES \
                and self.peek(1).type == TokenType.LESS:
            token = self.advance()
            collection_type = self.parse_collection_type(token)
            self.consume(TokenType.LPAREN, f"Expected '()' after {token.value}<...> to make an empty one")
            self.consume(TokenType.RPAREN, "Expected ')' - an empty collection takes no arguments "
                                           "(use [1, 2, 3] for a list with values)")
            return NewCollectionExpr(location=token.location, collection_type=collection_type)

        if self.check(TokenType.IDENTIFIER) or self.is_type_start() or self.check(TokenType.END):
            # Only consume if it's actually a valid identifier context
            # (not followed by another type keyword or invalid syntax)
            token = self.advance()
            return IdentifierExpr(
                location=token.location,
                name=token.value
            )

        # Keyword lambda (Task 18.1.3): func(int x) : x * 2  or  function(int x) : x * 2
        if self.check_any(TokenType.FUNC, TokenType.FUNCTION) and                 self.peek(1).type == TokenType.LPAREN:
            self.advance()  # func / function
            self.advance()  # (
            return self.parse_lambda()

        # Parenthesized expression or lambda
        if self.match(TokenType.LPAREN):
            # Lookahead to distinguish between (expr) and lambda (type name, ...) : body
            if self.is_lambda_start():
                return self.parse_lambda()

            # Regular parenthesized expression
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        # No valid primary expression found
        raise ParserError(
            self.peek(),
            f"Unexpected token '{self.peek().value}' - expected expression"
        )

    # ========================================================================
    # Lambda Expression Parsing
    # ========================================================================

    def is_lambda_start(self) -> bool:
        """Check if we're at the start of a lambda: (type name, ...) :

        Lookahead to find ':' after ')' at the same nesting level.
        Restores parser position after lookahead.

        Returns:
            True if current position starts a lambda expression
        """
        saved_pos = self.current
        depth = 1  # Already consumed opening (

        while not self.is_at_end() and depth > 0:
            token = self.peek()
            if token.type == TokenType.LPAREN:
                depth += 1
            elif token.type == TokenType.RPAREN:
                depth -= 1
                if depth == 0:
                    # Check if next token after ) is :
                    self.advance()
                    is_lambda = self.check(TokenType.COLON)
                    self.current = saved_pos
                    return is_lambda
            self.advance()

        self.current = saved_pos
        return False

    def parse_lambda(self) -> ASTNode:
        """Parse lambda expression: (int x, int y) : x + y

        Returns:
            LambdaExpr AST node
        """
        start_loc = self.previous().location  # Opening (

        # Parse parameter list
        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                parameters.append(self.parse_parameter())

        self.consume(TokenType.RPAREN, "Expected ')' after lambda parameters")
        self.consume(TokenType.COLON, "Expected ':' after lambda parameters")

        # Parse lambda body (a single expression - multi-line lambda bodies aren't
        # supported yet)
        body = self.parse_expression()

        # The return type isn't written in the source - the type checker infers it from
        # the body expression (None until then, Task 18.1.3)
        return LambdaExpr(
            location=start_loc,
            parameters=parameters,
            return_type=None,
            body=body
        )

    def parse_parameter(self) -> ParameterDecl:
        """Parse function/lambda parameter: type name = default_value

        Returns:
            ParameterDecl AST node
        """
        # `let int a` - can't be changed inside the function; `var int a` - can (the
        # default) - Task 46.1. The type is written: one from each caller is generics (33)
        is_let = False
        if self.check(TokenType.LET) or self.check(TokenType.VAR):
            keyword = self.advance()
            is_let = keyword.type == TokenType.LET
            if self.check(TokenType.IDENTIFIER) and self.peek(1).type in (
                    TokenType.COMMA, TokenType.RPAREN, TokenType.ASSIGN):
                raise ParserError(self.peek(), f"Give the parameter's type: {keyword.value} int "
                                               f"{self.peek().value} - a type taken from each "
                                               f"caller comes with generics (Task 33)")
        # `byVal List<int> xs` - a copy; `byRef` - shared (Task 32.10a)
        # `readonly Account a` - the function reads it, never changes it (Task 32.2e)
        is_readonly = self.check(TokenType.IDENTIFIER) and self.peek().value == 'readonly' \
            and self.peek(1).type != TokenType.COMMA and self.peek(1).type != TokenType.RPAREN
        if is_readonly:
            self.advance()
            if is_let or self._passing_word() is not None:
                raise ParserError(self.peek(), "'readonly' stands alone - it already means the "
                                               "function can't change the value")
        passing = self._passing_word()
        if passing is not None:
            self.advance()
        # Parse type (for now, just expect identifier for type name)
        param_type = self.parse_type()
        # `string... args` - any number of values, as an array (Task 18.5.4)
        variadic = self.match(TokenType.RANGE)
        if variadic:
            param_type = ArrayType(location=param_type.location, element_type=param_type, size=None)

        # Parse parameter name (allow keywords as parameter names)
        # This allows parameters named "end", "double", "string", etc.
        if self.check(TokenType.IDENTIFIER) or self.is_type_start() or self.check(TokenType.END):
            name_token = self.advance()
            name = name_token.value
        else:
            raise ParserError(self.peek(), "Expected parameter name")

        # Parse optional default value
        default_value = None
        if self.match(TokenType.ASSIGN):
            default_value = self.parse_expression()

        return ParameterDecl(
            location=param_type.location,
            by_val=passing is True,
            written_by_ref=passing is False,
            is_let=is_let,
            is_readonly=is_readonly,
            is_variadic=variadic,
            param_type=param_type,
            name=name,
            default_value=default_value
        )

    def parse_type(self) -> TypeNode:
        """Parse type annotation: int, float, double, string, bool, char, void, a struct
        name (Point, Task 18.2.1), or an array of one of those: int[], int[5]

        A struct name is just an identifier here - the parser can't know whether a struct of
        that name exists (it may be declared later in the file); the name resolver checks.

        Array size, if given, must be an integer literal for now (e.g. `int[5]`) - an
        arbitrary size expression (`int[n]`) is not yet supported. Multi-dimensional
        arrays (`int[][]`) are not yet supported either - see taskSummary2.md Task 9.

        Returns:
            TypeNode (PrimitiveType, or ArrayType wrapping one, for MVP)
        """
        # Function type (Task 18.1.3): (int, int) : int  or  (int, int) -> int
        if self.check(TokenType.LPAREN):
            return self.parse_function_type()

        # Otherwise a primitive type or a struct name (optionally as an array)
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                      TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
                      TokenType.VOID, TokenType.BYTE):
            token = self.previous()
            base_type = PrimitiveType(
                location=token.location,
                name=token.value
            )
        elif self.match(TokenType.IDENTIFIER):
            token = self.previous()
            name = token.value
            # A struct from another module: money.Price (Task 18.4.2)
            while self.check(TokenType.DOT) and self.peek(1).type == TokenType.IDENTIFIER:
                self.advance()
                name += '.' + self.advance().value
            if name in COLLECTION_TYPE_NAMES and self.check(TokenType.LESS):
                base_type = self.parse_collection_type(token)
            elif name == 'bytes':
                # Raw bytes (Task 18.3.8) - a built-in type, not a keyword
                base_type = PrimitiveType(location=token.location, name='bytes')
            else:
                base_type = StructType(location=token.location, name=name)
        else:
            base_type = None

        if base_type is not None:
            if self.match(TokenType.LBRACKET):
                size = None
                if not self.check(TokenType.RBRACKET):
                    size_token = self.consume(
                        TokenType.INTEGER,
                        "Array size must be an integer literal, e.g. int[5]"
                    )
                    size = integer_value(size_token.value)
                self.consume(TokenType.RBRACKET, "Expected ']' after array size")

                if self.check(TokenType.LBRACKET):
                    raise ParserError(
                        self.peek(),
                        "Multi-dimensional arrays are not yet supported"
                    )

                return ArrayType(
                    location=base_type.location,
                    element_type=base_type,
                    size=size
                )

            return base_type

        raise ParserError(
            self.peek(),
            f"Expected type name, got '{self.peek().value}'"
        )

    def parse_function_type(self) -> FunctionType:
        """Parse a function type: (int, int) : int, or the alternative (int, int) -> int
        (Task 18.1.3). Used for variables and parameters that hold a function.

        Returns:
            FunctionType AST node
        """
        start = self.consume(TokenType.LPAREN, "Expected '(' to start a function type")
        parameter_types = []
        if not self.check(TokenType.RPAREN):
            parameter_types.append(self.parse_type())
            while self.match(TokenType.COMMA):
                parameter_types.append(self.parse_type())
        self.consume(TokenType.RPAREN, "Expected ')' after function type parameters")
        if not self.match(TokenType.COLON, TokenType.ARROW):
            raise ParserError(self.peek(), "Expected ':' or '->' before function type's return type")
        return_type = self.parse_type()
        return FunctionType(
            location=start.location,
            parameter_types=parameter_types,
            return_type=return_type
        )

    def is_struct_type_declaration_start(self) -> bool:
        """Check whether a declaration with a struct type starts here (Task 18.2.1) - e.g.
        `Point p`, `Point[3] pts`, or at top level `Point function origin()`.

        A struct type is a plain identifier, so `Point p` has to be told apart from an
        expression statement that also starts with an identifier (`x = 5`, `print(x)`,
        `arr[0] = 1`). Two identifiers in a row never form an expression, so an identifier
        type followed by a name (or `function`) can only be a declaration.

        Returns:
            True if a struct type followed by a name or `function` starts here
        """
        if not self.check(TokenType.IDENTIFIER):
            return False
        offset = 1
        # List<int> xs, Map<string, int> ages (Task 18.5)
        if self.peek().value in COLLECTION_TYPE_NAMES and self.peek(1).type == TokenType.LESS:
            offset = self._skip_type_arguments(1)
            if offset < 0:
                return False
        # money.Price p - a struct from another module (Task 18.4.2)
        while self.peek(offset).type == TokenType.DOT and self.peek(offset + 1).type == TokenType.IDENTIFIER:
            offset += 2
        if self.peek(offset).type == TokenType.LBRACKET:
            offset += 1
            if self.peek(offset).type == TokenType.INTEGER:
                offset += 1
            if self.peek(offset).type != TokenType.RBRACKET:
                return False
            offset += 1
        if self.peek(offset).type == TokenType.COMMA and self.peek(offset + 1).value == 'Error' \
                and self.peek(offset + 2).type == TokenType.FUNCTION:
            return True                                # Ship, Error function (Task 26)
        return self.peek(offset).type in (TokenType.IDENTIFIER, TokenType.FUNCTION)

    def parse_collection_type(self, name_token) -> TypeNode:
        """The type arguments of a built-in collection, after its name (Task 18.5):
        List<int>, Map<string, int> - Dictionary is another name for Map."""
        self.consume(TokenType.LESS, f"Expected '<' after '{name_token.value}'")
        arguments = [self.parse_type()]
        while self.match(TokenType.COMMA):
            arguments.append(self.parse_type())
        self.consume(TokenType.GREATER, f"Expected '>' to close {name_token.value}<...>")
        expected = 1 if name_token.value == 'List' else 2
        if len(arguments) != expected:
            raise ParserError(name_token, f"{name_token.value} takes {expected} type"
                                          f"{'s' if expected > 1 else ''} in <...>, got {len(arguments)}")
        if name_token.value == 'List':
            return ListType(location=name_token.location, element_type=arguments[0])
        return MapType(location=name_token.location, key_type=arguments[0], value_type=arguments[1])

    def _skip_type_arguments(self, offset: int) -> int:
        """The offset just past `<...>` starting at `offset` (nested ones too), or -1."""
        depth = 0
        while True:
            kind = self.peek(offset).type
            if kind == TokenType.LESS:
                depth += 1
            elif kind == TokenType.GREATER:
                depth -= 1
                if depth == 0:
                    return offset + 1
            elif kind in (TokenType.NEWLINE, TokenType.EOF, TokenType.ASSIGN, TokenType.LPAREN):
                return -1
            offset += 1

    def is_function_type_declaration_start(self) -> bool:
        """Check whether a declaration with a function type starts here - e.g.
        `(int) : int op = ...` or `(int) : int function pick(...)`.

        Speculatively parses a function type and requires a name (or `function`) after it,
        then restores the position. This tells a declaration apart from an expression
        statement that also starts with '(' - `(a + b)` or a lambda `(int x) : x * 2` both
        fail the function-type parse.

        Returns:
            True if a function type followed by a name or `function` starts here
        """
        if not self.check(TokenType.LPAREN):
            return False
        saved_pos = self.current
        try:
            self.parse_function_type()
            return self.check(TokenType.IDENTIFIER) or self.check(TokenType.FUNCTION)
        except ParserError:
            return False
        finally:
            self.current = saved_pos

    # ========================================================================
    # Interpolated String Parsing
    # ========================================================================

    def parse_interpolated_string_from_parts(self, token: Token, parts: list) -> ASTNode:
        """Parse interpolated string from parts list.

        Builds a single ordered list of segments (StringTextPart / StringExprPart) rather
        than splitting text and expressions into two parallel arrays - see taskSummary2.md
        Task 12.4. The lexer already hands over an ordered, tagged sequence; this just
        carries that order onto the AST node instead of discarding it.

        Args:
            token: Original string token
            parts: List of [type, value] pairs from lexer

        Returns:
            InterpolatedStringExpr or LiteralExpr
        """
        segments: List[Union[StringTextPart, StringExprPart, StringPositionalPart]] = []
        has_interpolation = False

        for part_type, part_value in parts:
            if part_type == "STRING_PART":
                segments.append(StringTextPart(text=part_value))
            elif part_type == "INTERP_POS":
                # {@1}: a placeholder for print's first extra argument (Task 18.2.2b). It used
                # to be parsed as the expression `1`, so print("{@1}") printed "1"
                has_interpolation = True
                segments.append(StringPositionalPart(index=int(part_value)))
            elif part_type in ("INTERP_VAR", "INTERPOLATION"):
                # INTERP_VAR: {varname} or {point.x}, INTERPOLATION: legacy
                has_interpolation = True
                # Tokenize and parse the embedded expression
                from src.lexer.lexer import Lexer
                lexer = Lexer(part_value, token.location.filename)
                expr_tokens = lexer.tokenize()
                expr_parser = Parser(expr_tokens)
                expr = expr_parser.parse_expression()
                self.place_at(expr, token.location)
                segments.append(StringExprPart(expression=expr))

        # No interpolation? Return simple literal
        if not has_interpolation:
            text = ''.join(seg.text for seg in segments if isinstance(seg, StringTextPart))
            return LiteralExpr(
                location=token.location,
                value=text,
                type_hint="string"
            )

        return InterpolatedStringExpr(
            location=token.location,
            segments=segments
        )

    # ========================================================================
    # Statement Parsing
    # ========================================================================

    def parse_statement(self) -> ASTNode:
        """Parse any statement (entry point for statements).

        Returns:
            Statement AST node

        Raises:
            ParserError: If statement is malformed
        """
        # Return statement
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()

        # Break statement
        if self.match(TokenType.BREAK):
            return self.parse_break_statement()

        # Continue statement
        if self.match(TokenType.CONTINUE):
            return self.parse_continue_statement()

        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_statement()

        # While loop
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()

        # For loop
        if self.match(TokenType.FOR):
            return self.parse_for_statement()

        # match (Task 25.3); `fall match` falls through until break (Task 30.13) - `fall` is
        # a word only right before `match`
        if self.match(TokenType.MATCH):
            return self.parse_match_statement()
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'fall' \
                and self.peek(1).type == TokenType.MATCH:
            self.advance()
            self.advance()
            statement = self.parse_match_statement()
            statement.falls = True
            return statement

        # unchecked block (Task 27.2d) - `unchecked` is a word only before a block
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'unchecked' \
                and self.peek(1).type in (TokenType.NEWLINE, TokenType.LBRACE, TokenType.INDENT):
            unchecked_token = self.advance()
            while self.match(TokenType.NEWLINE):
                pass
            if not (self.check(TokenType.INDENT) or self.check(TokenType.LBRACE)):
                raise ParserError(self.peek(), "Expected the unchecked block - an indented "
                                               "block or '{' ... '}'")
            body = self.parse_block_statement()
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(TokenType.END) and self.peek(1).value == 'unchecked':
                self.advance()
                self.advance()
            return UncheckedStmt(location=unchecked_token.location, body=body)

        # try / catch / finally, throw (Task 26.3)
        if self.match(TokenType.TRY):
            return self.parse_try_statement()
        if self.match(TokenType.THROW):
            throw_token = self.previous()
            value = self.parse_expression()
            self.reject_compare_with_single_equals()   # Task 27.2
            self.consume_statement_terminator()
            return ThrowStmt(location=throw_token.location, value=value)

        # Block statement
        if self.check(TokenType.LBRACE) or self.check(TokenType.INDENT):
            return self.parse_block_statement()

        # Variable declaration or assignment or expression statement
        return self.parse_simple_statement()

    def parse_simple_statement(self) -> ASTNode:
        """Parse simple statements: var decl, const decl, assignment, or expression.

        Returns:
            Statement AST node (VarDeclStmt, AssignmentStmt, or ExpressionStmt)
        """
        # Check if it's a const declaration
        if self.check(TokenType.CONST):
            return self.parse_const_declaration()

        # `let x = 5` / `var x = 5` - the type comes from the value (Task 46.1)
        if self.check(TokenType.LET) or self.check(TokenType.VAR):
            return self.parse_inferred_declaration()

        # `template string greet = "Hello {@1}"` (Task 29.3)
        if self.is_template_start():
            return self.parse_template_declaration()

        # Check if it's a variable declaration (starts with type)
        if (self.is_type_start() or self.is_function_type_declaration_start()
                or self.is_struct_type_declaration_start()):
            return self.parse_var_declaration()

        # Otherwise, parse as expression (could be assignment)
        expr = self.parse_expression()

        # Check for assignment: expr = value
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
            self.reject_compare_with_single_equals()   # Task 27.2
            self.consume_statement_terminator()
            return AssignmentStmt(
                location=expr.location,
                target=expr,
                value=value
            )

        # Expression statement
        self.consume_statement_terminator()
        return ExpressionStmt(
            location=expr.location,
            expression=expr
        )

    def parse_var_declaration(self) -> ASTNode:
        """Parse variable declaration: int x = 5

        Returns:
            VarDeclStmt AST node
        """
        var_type = self.parse_type()

        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        location = name_token.location
        if self.check(TokenType.LBRACKET):
            # C-style `int numbers[]` - planned (Task 30.10); it used to be read silently as a
            # plain int followed by an empty list (Task 30.0)
            raise ParserError(self.peek(), f"Write the array type before the name: "
                                           f"{getattr(var_type, "name", "T")}[] {name} (the C-style "
                                           f"'{name}[]' is planned)")

        # `Ship s, Error err = loadShip(f)` - capture the call's error (Task 26)
        error_name, error_location, error_type = None, None, None
        if self.match(TokenType.COMMA):
            # `Ship s, err = ...` - the type is optional: it is always an Error (Task 26.8);
            # `Ship s, FileError err = ...` - an error type (26.10)
            if not (self.check(TokenType.IDENTIFIER) and self.peek(1).type == TokenType.ASSIGN):
                offset = 1
                while self.peek(offset).type == TokenType.DOT and self.peek(offset + 1).type == TokenType.IDENTIFIER:
                    offset += 2                       # files.FileError err
                if not (self.check(TokenType.IDENTIFIER) and self.peek(offset).type == TokenType.IDENTIFIER):
                    raise ParserError(self.peek(), "After ',' a declaration names the variable "
                                                   "that captures the error: Ship s, err = loadShip(f)")
                error_type = self.parse_type()
            error_token = self.consume(TokenType.IDENTIFIER, "Expected the error variable's name")
            error_name, error_location = error_token.value, error_token.location
            if not self.check(TokenType.ASSIGN):
                raise ParserError(self.peek(), f"'{name}, {error_name}' needs a call to capture: "
                                               f"... = loadShip(f)")

        # Optional initializer
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()
            self.reject_compare_with_single_equals()   # Task 27.2

        setup = self._setup_block(initializer is not None and error_name is None)

        return VarDeclStmt(
            location=location,
            var_type=var_type,
            name=name,
            initializer=initializer,
            error_name=error_name,
            error_location=error_location,
            error_type=error_type,
            setup=setup
        )

    def parse_inferred_declaration(self) -> VarDeclStmt:
        """`let name = readLine()` / `var count = 0` (Task 46.1): the type comes from the
        value. `let` is set once and never changes - the value may come later (`let total`,
        then `total = ...` on every path); `var` can change, its type can't."""
        keyword = self.advance()
        if self.is_type_start() and self.peek(1).type == TokenType.IDENTIFIER:
            raise ParserError(self.peek(), f"'{keyword.value}' takes its type from the value - "
                                           f"write {keyword.value} {self.peek(1).value} = ..., or "
                                           f"give the type instead: {self.peek().value} "
                                           f"{self.peek(1).value} = ...")
        name_token = self.consume(TokenType.IDENTIFIER, f"Expected the name after '{keyword.value}'")
        if self.check(TokenType.LBRACKET):
            raise ParserError(self.peek(), f"'{keyword.value}' takes its type from the value - "
                                           f"write {keyword.value} {name_token.value} = [1, 2, 3]")
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()
            self.reject_compare_with_single_equals()   # Task 27.2
        setup = self._setup_block(initializer is not None)
        return VarDeclStmt(location=name_token.location, var_type=None, name=name_token.value,
                           initializer=initializer, inferred=keyword.value, setup=setup)

    def _setup_block(self, has_value: bool):
        """Form B (Tasks 32.2c, 32.2d): a block right after a declaration's value sets that
        variable up further - `Car c = new Car() { c.speed = 4 }`. Ends the statement; returns
        the block, or None when there is none."""
        if has_value and (self.check(TokenType.LBRACE) or (
                self.check(TokenType.NEWLINE) and self.peek(1).type == TokenType.INDENT)):
            while self.match(TokenType.NEWLINE):
                pass
            block = self.parse_block_statement()
            while self.match(TokenType.NEWLINE):
                pass
            return block
        self.consume_statement_terminator()
        return None

    def parse_const_declaration(self) -> ASTNode:
        """Parse const declaration: const int x = 5

        Const declarations must have an initializer.

        Returns:
            VarDeclStmt AST node with is_const=True

        Raises:
            ParserError: If const declaration lacks initializer
        """
        const_token = self.consume(TokenType.CONST, "Expected 'const'")
        location = const_token.location

        var_type = self.parse_type()

        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value

        # Const requires initializer
        if not self.check(TokenType.ASSIGN):
            raise ParserError(name_token, "const declaration must have an initializer")

        self.consume(TokenType.ASSIGN, "Expected '=' after const variable name")
        initializer = self.parse_expression()
        self.reject_compare_with_single_equals()   # Task 27.2

        setup = self._setup_block(True)

        return VarDeclStmt(
            location=location,
            var_type=var_type,
            name=name,
            initializer=initializer,
            is_const=True,
            setup=setup
        )

    def parse_return_statement(self) -> ASTNode:
        """Parse return statement: return value

        Returns:
            ReturnStmt AST node
        """
        return_token = self.previous()  # RETURN token

        # Optional return value
        value = None
        if not self.check(TokenType.NEWLINE) and not self.is_block_end():
            value = self.parse_expression()
            self.reject_compare_with_single_equals()   # Task 27.2

        self.consume_statement_terminator()

        return ReturnStmt(
            location=return_token.location,
            value=value
        )

    def parse_break_statement(self) -> ASTNode:
        """Parse break statement: break

        Returns:
            BreakStmt AST node
        """
        break_token = self.previous()  # BREAK token
        self.consume_statement_terminator()

        return BreakStmt(
            location=break_token.location
        )

    def parse_continue_statement(self) -> ASTNode:
        """Parse continue statement: continue

        Returns:
            ContinueStmt AST node
        """
        continue_token = self.previous()  # CONTINUE token
        self.consume_statement_terminator()

        return ContinueStmt(
            location=continue_token.location
        )

    def parse_if_statement(self) -> ASTNode:
        """Parse if statement: if condition { body } else { else_body }

        Returns:
            IfStmt AST node
        """
        if_token = self.previous()  # IF token

        # Condition
        condition = self.parse_condition()

        # Skip newlines after condition
        while self.match(TokenType.NEWLINE):
            pass

        # Then branch (block)
        then_branch = self.parse_block_statement()

        # Optional else branch
        else_branch = None
        if self.match(TokenType.ELSE):
            # Skip newlines after else
            while self.match(TokenType.NEWLINE):
                pass

            # Else can be followed by if (elif) or block
            if self.match(TokenType.IF):
                else_branch = self.parse_if_statement()
            else:
                else_branch = self.parse_block_statement()

        # Check for End if (if using End keyword style)
        if self.match(TokenType.END):
            self.consume(TokenType.IF, "Expected 'if' after 'End'")

        return IfStmt(
            location=if_token.location,
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )

    def parse_match_statement(self) -> ASTNode:
        """Parse a match statement (Task 25.3), indented, braced or closed by `End match`:

            match light                     match ch {
                case Red, Yellow                case '+', '-' {
                    print("stop")                   print("operator")
                case Green: print("go")         }
                                                else: print("other")
                                            }

        A case body is a block, or one statement after `:`. `else` catches the rest.
        The MATCH token has already been consumed."""
        match_token = self.previous()
        subject = self.parse_expression()
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.LBRACE):
            closing = TokenType.RBRACE
        elif self.match(TokenType.INDENT):
            closing = TokenType.DEDENT
        else:
            raise ParserError(self.peek(), "Expected the cases of 'match' - an indented block "
                                           "of 'case' lines, or '{' ... '}'")
        cases, else_body = [], None
        while True:
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(closing) or self.is_at_end():
                break
            if else_body is not None:
                raise ParserError(self.peek(), "'else' must be the last part of a match")
            if self.match(TokenType.ELSE) or self._match_anything_else():
                else_body = self.parse_case_body()
                continue
            if self.check(TokenType.IDENTIFIER) or self.check(TokenType.INTEGER) \
                    or self.check(TokenType.STRING) or self.check(TokenType.CHAR):
                raise ParserError(self.peek(), "Each part of a match statement starts with "
                                               "'case' - a match without 'case' gives a value, "
                                               "and is assigned: string s = match n { 1 : \"a\", "
                                               "_ : \"b\" }")
            case_token = self.consume(TokenType.CASE, "Expected 'case' or 'else' inside 'match'")
            patterns = [self.parse_match_pattern()]
            while self.match(TokenType.COMMA):
                patterns.append(self.parse_match_pattern())
            cases.append(MatchCase(location=case_token.location, patterns=patterns,
                                   body=self.parse_case_body()))
        self.consume(closing, "Expected the end of 'match'")
        while self.match(TokenType.NEWLINE):
            pass
        if self.check(TokenType.END) and self.peek(1).type == TokenType.MATCH:
            self.advance()
            self.advance()
        if not cases:
            raise ParserError(match_token, "A match needs at least one 'case'")
        return MatchStmt(location=match_token.location, subject=subject, cases=cases,
                         else_body=else_body)

    def _match_anything_else(self) -> bool:
        """`_` (or `case _`) where `else` may go - "anything else" (Task 46.2)."""
        ends = (TokenType.COLON, TokenType.NEWLINE, TokenType.LBRACE, TokenType.INDENT)
        if self.check(TokenType.IDENTIFIER) and self.peek().value == '_' \
                and self.peek(1).type in ends:
            self.advance()
            return True
        if self.check(TokenType.CASE) and self.peek(1).type == TokenType.IDENTIFIER \
                and self.peek(1).value == '_' and self.peek(2).type in ends:
            self.advance()
            self.advance()
            return True
        return False

    def parse_match_value(self) -> MatchExpr:
        """A match that gives a value - form A (Task 46.2):

            match n { 6, 7 : "Weekend", _ : "Weekday" }        match count
                                                                   0 : "none"
                                                                   _ : "some"

        Each case: values, `:`, one value. `_` or `else` for anything else. The MATCH token
        has already been consumed."""
        match_token = self.previous()
        subject = self.parse_expression()
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.LBRACE):
            closing = TokenType.RBRACE
        elif self.match(TokenType.INDENT):
            closing = TokenType.DEDENT
        else:
            raise ParserError(self.peek(), "Expected the cases of the match - "
                                           "{ 1 : \"one\", _ : \"other\" }, or an indented block")
        skip = (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT) \
            if closing == TokenType.RBRACE else (TokenType.NEWLINE,)
        cases, else_value = [], None
        while True:
            while self.match(*skip):
                pass
            if self.check(closing) or self.is_at_end():
                break
            if else_value is not None:
                raise ParserError(self.peek(), "'_' (or else) must be the last case of a match")
            if self.check(TokenType.CASE):
                raise ParserError(self.peek(), "A match that gives a value has no 'case' - "
                                               "write 6, 7 : \"Weekend\"; a match with 'case' is "
                                               "a statement and can't be assigned")
            location = self.peek().location
            if self.match(TokenType.ELSE) or self._match_anything_else():
                self.consume(TokenType.COLON, "Expected ':' and the value")
                else_value = self.parse_expression()
            else:
                patterns = [self.parse_match_pattern()]
                while self.match(TokenType.COMMA):
                    patterns.append(self.parse_match_pattern())
                self.consume(TokenType.COLON, "Expected ':' and the value after the case's values")
                cases.append(MatchArm(location=location, patterns=patterns,
                                      value=self.parse_expression()))
            if self.check(TokenType.COMMA):
                self.advance()
            elif not (self.check(closing) or self.check(TokenType.NEWLINE)
                      or (closing == TokenType.RBRACE and self.check(TokenType.DEDENT))):
                raise ParserError(self.peek(), "A case of a match value is one value - no code; "
                                               "a function call can fetch it")
        self.consume(closing, "Expected the end of the match")
        if closing == TokenType.DEDENT:
            self.block_value_end = self.current     # the line ended with the block
        if not cases and else_value is None:
            raise ParserError(match_token, "A match needs at least one case")
        return MatchExpr(location=match_token.location, subject=subject, cases=cases,
                         else_body=else_value)

    def parse_try_statement(self) -> ASTNode:
        """Parse try / catch err / finally (Task 26.3), indented, braced or closed by
        `End try`. A try needs a catch, a finally, or both. The TRY token is consumed."""
        try_token = self.previous()
        body = self._try_part_block('try')
        node = TryStmt(location=try_token.location, body=body)
        self._skip_newlines_before(TokenType.CATCH, TokenType.FINALLY)
        while self.match(TokenType.CATCH):
            clause = CatchClause(location=self.previous().location)
            if self.check(TokenType.IDENTIFIER):
                # `catch FileError e` (a type, then the name - Task 26.11) or `catch e`
                offset = 1
                while self.peek(offset).type == TokenType.DOT and self.peek(offset + 1).type == TokenType.IDENTIFIER:
                    offset += 2
                if self.peek(offset).type == TokenType.IDENTIFIER:
                    clause.error_type = self.parse_type()
                clause.name = self.consume(TokenType.IDENTIFIER, "Expected the error's name").value
            clause.body = self._try_part_block('catch')
            node.catches.append(clause)
            self._skip_newlines_before(TokenType.CATCH, TokenType.FINALLY)
        if self.match(TokenType.FINALLY):
            node.finally_body = self._try_part_block('finally')
        if not node.catches and node.finally_body is None:
            raise ParserError(try_token, "A try needs a 'catch', a 'finally', or both")
        while self.match(TokenType.NEWLINE):
            pass
        if self.check(TokenType.END) and self.peek(1).type == TokenType.TRY:
            self.advance()
            self.advance()
        return node

    def _try_part_block(self, part: str) -> BlockStmt:
        while self.match(TokenType.NEWLINE):
            pass
        if not (self.check(TokenType.INDENT) or self.check(TokenType.LBRACE)):
            raise ParserError(self.peek(), f"Expected the {part} block - an indented block "
                                           f"or '{{' ... '}}'")
        return self.parse_block_statement()

    def _skip_newlines_before(self, *token_types) -> None:
        """Skip blank lines only when one of token_types follows (`}` then `catch` on the
        next line, brace style)."""
        offset = 0
        while self.peek(offset).type == TokenType.NEWLINE:
            offset += 1
        if offset and self.peek(offset).type in token_types:
            for _ in range(offset):
                self.advance()

    def reject_compare_with_single_equals(self) -> None:
        """`bool same = a = b`: `=` compares only in a condition (if / while / else if) -
        elsewhere it stores, so a second one is a mistake (Task 27.2)."""
        if self.check(TokenType.ASSIGN):
            raise ParserError(self.peek(), "'=' compares only in a condition (if, while); to "
                                           "compare here write '==', e.g. bool same = a == b")

    def parse_case_body(self) -> BlockStmt:
        """A case's (or the else's) body: `: statement` on the same line, or a block."""
        if self.match(TokenType.COLON):
            location = self.peek().location
            return BlockStmt(location=location, statements=[self.parse_statement()])
        while self.match(TokenType.NEWLINE):
            pass
        if not (self.check(TokenType.INDENT) or self.check(TokenType.LBRACE)):
            raise ParserError(self.peek(), "Expected the body of the case - an indented block, "
                                           "'{' ... '}', or ':' and one statement")
        return self.parse_block_statement()

    def parse_match_pattern(self) -> MatchPattern:
        """`Red`, `Number(n)` (an enum value - its bare name) or a constant: 42, -1, 'x', "go";
        or `null` (Task 30.12)."""
        location = self.peek().location
        if self.match(TokenType.NULL):
            return MatchPattern(location=location, is_null=True)
        if self.check(TokenType.IDENTIFIER):
            name = self.advance().value
            dotted = False
            while self.check(TokenType.DOT) and self.peek(1).type == TokenType.IDENTIFIER:
                self.advance()
                name += '.' + self.advance().value    # an error type from a module (26.10)
                dotted = True
            if dotted:
                return MatchPattern(location=location, name=name, dotted=True)
            bindings = []
            if self.match(TokenType.LPAREN):
                while not self.check(TokenType.RPAREN) and not self.is_at_end():
                    bindings.append(self.consume(
                        TokenType.IDENTIFIER, "Expected a name for the value's data").value)
                    if not self.match(TokenType.COMMA):
                        break
                self.consume(TokenType.RPAREN, "Expected ')' after the names")
            return MatchPattern(location=location, name=name, bindings=bindings)
        return MatchPattern(location=location, value=self.parse_unary())

    def parse_while_statement(self) -> ASTNode:
        """Parse while loop: while condition { body }

        Returns:
            WhileStmt AST node
        """
        while_token = self.previous()  # WHILE token

        # Condition
        condition = self.parse_condition()

        # Skip newlines after condition
        while self.match(TokenType.NEWLINE):
            pass

        # Body
        body = self.parse_block_statement()

        # Check for End while (if using End keyword style)
        if self.match(TokenType.END):
            self.consume(TokenType.WHILE, "Expected 'while' after 'End'")

        return WhileStmt(
            location=while_token.location,
            condition=condition,
            body=body
        )

    def parse_for_statement(self) -> ASTNode:
        """Parse for loop: for i in range { body }

        Returns:
            ForStmt AST node
        """
        for_token = self.previous()  # FOR token

        # Loop variable
        var_token = self.consume(TokenType.IDENTIFIER, "Expected loop variable name")
        variable = var_token.value

        # 'in' keyword
        self.consume(TokenType.IN, "Expected 'in' after loop variable")

        # Iterable expression
        iterable = self.parse_expression()

        # Skip newlines after iterable
        while self.match(TokenType.NEWLINE):
            pass

        # Body
        body = self.parse_block_statement()

        # Check for End for (if using End keyword style)
        if self.match(TokenType.END):
            self.consume(TokenType.FOR, "Expected 'for' after 'End'")

        return ForStmt(
            location=for_token.location,
            variable=variable,
            iterable=iterable,
            body=body
        )

    def parse_block_statement(self) -> ASTNode:
        """Parse block statement (braces, indentation, or End keyword).

        Returns:
            BlockStmt AST node or single statement (for End keyword style)
        """
        start_loc = self.peek().location

        # Brace block: { stmt1; stmt2; }
        if self.match(TokenType.LBRACE):
            statements = []
            # Skip leading newlines
            while self.match(TokenType.NEWLINE):
                pass

            while not self.check(TokenType.RBRACE) and not self.is_at_end():
                statements.append(self.parse_statement())
                # Skip newlines between statements
                while self.match(TokenType.NEWLINE):
                    pass

            self.consume(TokenType.RBRACE, "Expected '}' after block")
            return BlockStmt(location=start_loc, statements=statements)

        # Indentation block: INDENT stmt1 stmt2 DEDENT
        if self.match(TokenType.INDENT):
            statements = []
            # Skip leading newlines
            while self.match(TokenType.NEWLINE):
                pass

            while not self.check(TokenType.DEDENT) and not self.is_at_end():
                statements.append(self.parse_statement())
                # Skip newlines between statements
                while self.match(TokenType.NEWLINE):
                    pass

            self.consume(TokenType.DEDENT, "Expected DEDENT after indented block")
            return BlockStmt(location=start_loc, statements=statements)

        # End keyword block: handled by caller (if/while/for)
        # Single statement without block
        stmt = self.parse_statement()
        return BlockStmt(location=start_loc, statements=[stmt])

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def consume_statement_terminator(self):
        """Consume optional newline after statement.

        Newlines and semicolons are optional in many contexts.
        In Fusion, statements are typically terminated by newlines or block boundaries.
        """
        # A statement ends the line, or its block: `int x = 5 print(x)` and `int n[]` used to be
        # read silently as two statements (Task 30.0)
        if not (self.check(TokenType.NEWLINE) or self.check(TokenType.RBRACE)
                or self.check(TokenType.DEDENT) or self.check(TokenType.END)
                or self.is_at_end() or getattr(self, 'block_value_end', None) == self.current):
            raise ParserError(self.peek(), f"Expected the end of the line after this statement, "
                                           f"found '{self.peek().value}' - one statement per line")
        while self.match(TokenType.NEWLINE):
            pass  # Skip newlines

    def is_block_end(self) -> bool:
        """Check if at end of block.

        Returns:
            True if at block ending token
        """
        return (self.check(TokenType.RBRACE) or
                self.check(TokenType.DEDENT) or
                self.check(TokenType.END) or
                self.check(TokenType.NEWLINE) or
                self.is_at_end())

    def is_type_start(self) -> bool:
        """Check if current token starts a type.

        Returns:
            True if current token is a type keyword
        """
        return self.check_any(
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
            TokenType.VOID, TokenType.BYTE
        )

    def check_any(self, *token_types: TokenType) -> bool:
        """Check if current token matches any type.

        Args:
            token_types: Variable number of TokenTypes to check

        Returns:
            True if current token matches any of the types
        """
        for token_type in token_types:
            if self.check(token_type):
                return True
        return False

    # ========================================================================
    # Program & Declaration Parsing
    # ========================================================================

    def parse_program(self) -> ASTNode:
        """Parse entire program (entry point for parser).

        Returns:
            ProgramNode containing all top-level declarations
        """
        start_loc = self.peek().location
        declarations = []

        # Skip leading newlines
        while self.match(TokenType.NEWLINE):
            pass

        # Imports come first (Task 18.4.2)
        imports = []
        while self.match(TokenType.IMPORT):
            imports.append(self.parse_import())
            while self.match(TokenType.NEWLINE):
                pass

        while not self.is_at_end():
            if self.check(TokenType.IMPORT):
                raise ParserError(self.peek(), "'import' lines must come before everything else "
                                               "in the file")
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
                # Types - structs, classes, enums - are public unless written private;
                # functions and module variables private unless written public (Task 32.2a)
                if isinstance(decl, (StructDecl, EnumDecl)) \
                        and not getattr(decl, 'visibility_written', False):
                    decl.is_public = True
                if isinstance(decl, StructDecl):
                    for method in decl.methods + decl.static_methods:   # Tasks 32.1, 32.2c
                        method.is_public = decl.is_public
                        declarations.append(method)

            # Skip newlines between declarations
            while self.match(TokenType.NEWLINE):
                pass

        return ProgramNode(
            location=start_loc,
            declarations=declarations,
            imports=imports
        )

    def parse_import(self) -> ImportDecl:
        """Parse an import line, the IMPORT token already consumed (Task 18.4.2):
        `import money`, `import money.Price`, `import money.*`, `import lib.utils as u`."""
        import_token = self.previous()
        path = [self.consume(TokenType.IDENTIFIER, "Expected a module name after 'import'").value]
        star = False
        while self.match(TokenType.DOT):
            if self.match(TokenType.MULTIPLY):
                star = True
                break
            path.append(self.consume(TokenType.IDENTIFIER,
                                     "Expected a name or '*' after '.' in an import").value)
        alias = None
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'as':
            self.advance()
            if star:
                raise ParserError(self.previous(), "'import ...*' can't have an 'as' name")
            alias = self.consume(TokenType.IDENTIFIER, "Expected a name after 'as'").value
        if not (self.check(TokenType.NEWLINE) or self.is_at_end()):
            raise ParserError(self.peek(), "Expected the end of the line after the import")
        return ImportDecl(location=import_token.location, path=path, star=star, alias=alias)

    def parse_declaration(self) -> Optional[ASTNode]:
        """Parse top-level declaration (function, var, etc.).

        Returns:
            Declaration AST node or None if no valid declaration found

        Raises:
            ParserError: If declaration is malformed
        """
        # `public` / `private` before a struct or function (Task 18.4.3) - private is the
        # default, so `private` only says so explicitly
        if self.match(TokenType.PUBLIC, TokenType.PRIVATE):
            modifier = self.previous()
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(TokenType.PUBLIC) or self.check(TokenType.PRIVATE):
                raise ParserError(self.peek(), "Only one of 'public' / 'private' may be given")
            if not (self.check(TokenType.STRUCT) or self.check(TokenType.ENUM)
                    or self.check(TokenType.CONST)
                    or self.is_error_declaration_start() or self.is_type_start()
                    or self.is_function_type_declaration_start()
                    or self.is_struct_type_declaration_start()):
                raise ParserError(modifier, f"'{modifier.value}' can only come before a struct, "
                                            f"an enum, a function or a module variable")
            decl = self.parse_declaration()
            if not isinstance(decl, (FunctionDecl, StructDecl, EnumDecl, ErrorDecl, VarDeclStmt)):
                raise ParserError(modifier, f"'{modifier.value}' can only come before a struct, "
                                            f"an enum, a function or a module variable")
            decl.is_public = modifier.type == TokenType.PUBLIC
            decl.visibility_written = True
            return decl

        # A module-level `let` / `var` (Task 46.1)
        if self.check(TokenType.LET) or self.check(TokenType.VAR):
            return self.parse_inferred_declaration()

        # A module-level constant: `const int LIMIT = 10` (Task 44.1)
        if self.match(TokenType.CONST):
            return self.parse_module_variable(self.parse_type(), is_const=True)

        # A module-level string template (Task 29.3)
        if self.is_template_start():
            return self.parse_template_declaration()

        # Struct declaration (Task 18.2.1)
        if self.match(TokenType.STRUCT):
            return self.parse_struct_declaration()

        # Class declaration (Task 32.10b)
        if self.match(TokenType.CLASS):
            return self.parse_class_declaration()

        # Enum declaration (Task 25)
        if self.match(TokenType.ENUM):
            return self.parse_enum_declaration()

        # Custom error type: `error FileError` (Task 26.9) - `error` is only special here
        if self.is_error_declaration_start():
            return self.parse_error_declaration()

        # Function declaration: <return_type> function <name>(<params>) { body }
        if (self.is_type_start() or self.is_function_type_declaration_start()
                or self.is_struct_type_declaration_start()):
            return_type = self.parse_type()

            # `Ship, Error function` - a function that can fail (Task 26)
            returns_error = False
            if self.check(TokenType.COMMA) and self.peek(1).value == 'Error':
                self.advance()
                self.advance()
                returns_error = True

            # A type and then a name: a module-level variable, `int count = 0` (Task 44.1)
            if not returns_error and self.check(TokenType.IDENTIFIER):
                return self.parse_module_variable(return_type, is_const=False)

            # Skip newlines after return type
            while self.match(TokenType.NEWLINE):
                pass

            if self.match(TokenType.FUNCTION):
                decl = self.parse_function_declaration(return_type)
                decl.returns_error = returns_error
                return decl

            # Could be a global variable declaration
            # For MVP, we might not support global vars
            raise ParserError(self.peek(), "Expected 'function' keyword after type")

        # Skip unexpected tokens (error recovery)
        raise ParserError(self.peek(), f"Unexpected token '{self.peek().value}' at top level")

    def parse_module_variable(self, var_type: TypeNode, is_const: bool) -> VarDeclStmt:
        """A variable or constant declared outside any function (Task 44.1): `int count = 0`,
        `const int LIMIT = 10`, `public string version = "1.0"`. The type has been read."""
        name_token = self.consume(TokenType.IDENTIFIER, "Expected the variable's name")
        if self.check(TokenType.COMMA):
            raise ParserError(self.peek(), "Capturing an error (`T x, err = f()`) only works "
                                           "inside a function")
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()
            self.reject_compare_with_single_equals()
        elif is_const:
            raise ParserError(name_token, "const declaration must have an initializer")
        self.consume_statement_terminator()
        return VarDeclStmt(location=name_token.location, var_type=var_type,
                           name=name_token.value, initializer=initializer, is_const=is_const)

    def parse_struct_declaration(self) -> StructDecl:
        """Parse a struct declaration (Task 18.2.1), in any of the three block styles:

            struct Point        struct Point {        struct Point
                int x               int x                 int x
                int y               int y                 int y
                                }                     End struct

        Fields only - each is `<type> <name>`, optionally `= <constant default>`. Structs are
        pure value types: no methods, operators or constructors (the compiler generates the
        only constructor). The STRUCT token has already been consumed.

        Returns:
            StructDecl AST node
        """
        struct_token = self.previous()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected struct name after 'struct'")

        # The struct it builds on (Task 32.8): implements, or extends / includes (not keywords)
        parent = None
        if self.match(TokenType.IMPLEMENTS) or (
                self.check(TokenType.IDENTIFIER) and self.peek().value in ('extends', 'includes')
                and self.advance()):
            parent = self.consume(TokenType.IDENTIFIER,
                                  f"Expected the struct that '{name_token.value}' builds on").value
            if self.check(TokenType.COMMA):
                raise ParserError(self.peek(), f"Struct '{name_token.value}' can build on one "
                                               f"struct only")

        while self.match(TokenType.NEWLINE):
            pass

        if self.match(TokenType.LBRACE):
            closing = TokenType.RBRACE
        elif self.match(TokenType.INDENT):
            closing = TokenType.DEDENT
        else:
            raise ParserError(
                self.peek(),
                f"Expected the fields of struct '{name_token.value}' - an indented block, or "
                f"'{{' ... '}}'"
            )

        fields, methods = [], []
        while self.match(TokenType.NEWLINE):
            pass
        while not self.check(closing) and not self.is_at_end():
            if self.check_any(TokenType.FUNCTION, TokenType.FUNC) or (
                    self.check(TokenType.IDENTIFIER) and self.peek().value == 'constructor'):
                raise ParserError(
                    self.peek(),
                    f"Struct '{name_token.value}' can't have a constructor - the compiler makes "
                    f"its only one; a method needs its return type first: void function "
                    f"move(int dx)"
                )
            item = self.parse_struct_field()
            (methods if isinstance(item, FunctionDecl) else fields).append(item)
            while self.match(TokenType.NEWLINE):
                pass

        self.consume(closing, f"Expected end of struct '{name_token.value}'")
        while self.match(TokenType.NEWLINE):
            pass

        # Optional `End struct` (End keyword style)
        if self.match(TokenType.END):
            self.consume(TokenType.STRUCT, "Expected 'struct' after 'End'")

        struct = StructDecl(location=struct_token.location, name=name_token.value, fields=fields,
                            parent=parent)
        self.attach_methods(struct, methods)
        return struct

    def parse_class_declaration(self) -> StructDecl:
        """`class Car` (Task 32.10b) - fields, methods and an optional constructor, in any
        block style:

            class Car
                string name
                Engine engine                   // an object: null until set
                constructor(string name)        // or Car(string name) - the same
                    this.name = name
                void function rename(string n)
                    name = n

        No constructor: `Car()` makes one with every field at its default. The constructor
        becomes the function `Car.new`: make the object, run the body, return it. The CLASS
        token has already been consumed."""
        class_token = self.previous()
        name = self.consume(TokenType.IDENTIFIER, "Expected the class name after 'class'").value
        if self.check(TokenType.IMPLEMENTS) or self.check(TokenType.INHERITS) or (
                self.check(TokenType.IDENTIFIER) and self.peek().value in ('extends', 'includes')):
            raise ParserError(self.peek(), "A class building on another class comes with "
                                           "inheritance (Task 32.7)")
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.LBRACE):
            closing = TokenType.RBRACE
        elif self.match(TokenType.INDENT):
            closing = TokenType.DEDENT
        else:
            raise ParserError(self.peek(), f"Expected the members of class '{name}' - an "
                                           f"indented block, or '{{' ... '}}'")
        fields, methods, constructors = [], [], []
        static_fields, static_methods, static_block = [], [], None
        while True:
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(closing) or self.is_at_end():
                break
            # public / private on a member (Task 32.2a): fields private, functions and
            # constructors public when nothing is written (Classes.md section 1)
            written = None
            if self.match(TokenType.PUBLIC, TokenType.PRIVATE):
                written = self.previous().type == TokenType.PUBLIC
            # Form C, the static block: `static { ... }` (Task 32.2c)
            if self.check(TokenType.STATIC) and self.peek(1).type in (
                    TokenType.LBRACE, TokenType.NEWLINE, TokenType.INDENT):
                start = self.advance()
                while self.match(TokenType.NEWLINE):
                    pass
                if static_block is not None:
                    raise ParserError(start, f"Class '{name}' has one static block - put its "
                                             f"set-up together")
                static_block = self.parse_block_statement()
                continue
            # `const` and `static`, in any order (Task 32.2c)
            is_const = is_static = False
            while self.check(TokenType.CONST) or self.check(TokenType.STATIC):
                if self.advance().type == TokenType.CONST:
                    is_const = True
                else:
                    is_static = True
            if is_const and not is_static:
                raise ParserError(self.previous(), "In a class, 'const' goes with 'static' - "
                                                   "const static Car CAR = Car()")
            if (self.check(TokenType.IDENTIFIER) and self.peek().value in ('constructor', name)
                    and self.peek(1).type == TokenType.LPAREN):
                start = self.advance()
                self.consume(TokenType.LPAREN, "Expected '('")
                parameters = []
                if not self.check(TokenType.RPAREN):
                    parameters.append(self.parse_parameter())
                    while self.match(TokenType.COMMA):
                        parameters.append(self.parse_parameter())
                self.consume(TokenType.RPAREN, "Expected ')' after the constructor's parameters")
                while self.match(TokenType.NEWLINE):
                    pass
                constructors.append((start, parameters, self.parse_block_statement(),
                                     written is False))
                continue
            item = self.parse_struct_field()
            if isinstance(item, FunctionDecl):
                item.is_private = written is False
                item.is_static = is_static
                (static_methods if is_static else methods).append(item)
                continue
            item.is_private = written is not True
            # Form B: a block right after a field's value sets it up further (32.2c, 32.2d)
            item.setup = None
            if item.default_value is not None and (self.check(TokenType.LBRACE) or (
                    self.check(TokenType.NEWLINE) and self.peek(1).type == TokenType.INDENT)):
                item.setup = self._setup_block(True)
            if not is_static:
                fields.append(item)
                continue
            item.is_static, item.is_const = True, is_const
            static_fields.append(item)
        self.consume(closing, f"Expected the end of class '{name}'")
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.END):
            self.consume(TokenType.CLASS, "Expected 'class' after 'End'")
        decl = StructDecl(location=class_token.location, name=name, fields=fields, is_class=True,
                          static_fields=static_fields, static_block=static_block)
        self.attach_methods(decl, methods)
        for method in static_methods:                # no `this` (Task 32.2c)
            method.method_name, method.method_of = method.name, name
            method.name = f'{name}.{method.name}'
            method.changes_this = False
        decl.static_methods = static_methods
        for method in decl.methods:
            method.parameters[0].by_ref = False      # `this` is a reference already
        # Several constructors (Task 32.2b): Car.new, Car.new_2, ... - a call picks one by
        # its arguments
        for number, written in enumerate(constructors or [None], start=1):
            decl.methods.append(self._constructor(decl, written, number))
        return decl

    def _constructor(self, decl: StructDecl, written, number: int = 1) -> FunctionDecl:
        """`Car.new(...)`: `Car this = <a new Car>`, the constructor's body, `return this`. A
        bare `return` in the body returns the object. A parameter may have a field's name
        (`this.name = name` - Java's habit): then the bare name is the parameter. With
        `this(...)` on the first line another constructor makes the object (Task 32.2b):
        `Car this = Car(...)`, then this one's body goes on."""
        location = written[0].location if written else decl.location
        parameters, body = (written[1], written[2]) if written else \
            ([], BlockStmt(location=location, statements=[]))
        private = bool(written and written[3])
        # a new type node for each use - the module loader rewrites each one in place
        class_type = lambda: StructType(location=location, name=decl.name)
        this = lambda: IdentifierExpr(location=location, name='this')
        method = FunctionDecl(location=location, name=decl.name, parameters=parameters,
                              return_type=class_type(), body=body)
        delegate = self._this_call(body.statements[0]) if body.statements else None
        if delegate is not None:
            body.statements = body.statements[1:]
        for statement in body.statements:
            if self._this_call(statement) is not None:
                raise ParserError(self.previous(), "this(...) calls another constructor only on "
                                                   "a constructor's first line")
        field_names = {f.name for f in decl.fields} - {p.name for p in parameters}
        if delegate is not None:
            used = self._names_in(delegate.arguments)
            clash = sorted(used & (field_names | {'this'}))
            if clash:
                raise ParserError(self.previous(), f"this(...) can't use '{clash[0]}' - the object "
                                                   f"isn't made until the other constructor runs")
        method_names = {m.method_name for m in decl.methods}
        if delegate is None:
            body.statements = self._field_setups(decl, method_names) + body.statements
        self.rewrite_method_body(method, decl.name, field_names, method_names,
                                 lambda message: self._fail(message))

        def returns(node):
            if isinstance(node, ReturnStmt) and node.value is None:
                node.value = this()
            elif isinstance(node, list):
                for item in node:
                    returns(item)
            elif is_dataclass(node) and not isinstance(node, (type, LambdaExpr)):
                for f in dataclass_fields(node):
                    if f.name not in ('location', 'inferred_type', 'scope'):
                        returns(getattr(node, f.name))

        returns(body)
        made = ObjectMakeExpr(location=location, class_type=class_type()) if delegate is None \
            else CallExpr(location=delegate.location, arguments=delegate.arguments,
                          callee=IdentifierExpr(location=delegate.location, name=decl.name))
        body.statements = ([VarDeclStmt(location=location, var_type=class_type(), name='this',
                                        initializer=made)]
                           + body.statements + [ReturnStmt(location=location, value=this())])
        method.method_name = 'new'
        method.method_of = decl.name
        method.is_constructor = True
        method.is_private = private
        method.changes_this = False
        method.delegate = made if delegate is not None else None
        method.name = f'{decl.name}.new' if number == 1 else f'{decl.name}.new_{number}'
        return method

    def _field_setups(self, decl: StructDecl, method_names) -> list:
        """A class field whose value isn't a plain constant, or that has a form B block (Task
        32.2d), is set by each constructor first, in field order: `this.engine = new
        Engine()`, then its block - before the constructor's own body."""
        statements = []
        every_field = {f.name for f in decl.fields}
        for f in decl.fields:
            value = getattr(f, 'moved_default', None) or f.default_value
            if value is None or (getattr(f, 'setup', None) is None and (
                    isinstance(value, LiteralExpr) or (isinstance(value, UnaryExpr)
                                                       and isinstance(value.operand, LiteralExpr)))):
                continue
            f.moved_default, f.default_value = value, None   # the object starts it at zero
            block = BlockStmt(location=f.location, statements=[AssignmentStmt(
                location=f.location, target=IdentifierExpr(location=f.location, name=f.name),
                value=copy.deepcopy(value))])
            if getattr(f, 'setup', None) is not None:
                block.statements.append(copy.deepcopy(f.setup))
            holder = FunctionDecl(location=f.location, name=f'{decl.name}.new', parameters=[],
                                  return_type=None, body=block)
            self.rewrite_method_body(holder, decl.name, every_field, method_names,
                                     lambda message: self._fail(message))
            statements += block.statements
        return statements

    @staticmethod
    def _this_call(statement):
        """The call in `this(...)` - a constructor calling another - or None."""
        if isinstance(statement, ExpressionStmt) and isinstance(statement.expression, CallExpr) \
                and isinstance(statement.expression.callee, IdentifierExpr) \
                and statement.expression.callee.name == 'this':
            return statement.expression
        return None

    @classmethod
    def _names_in(cls, node) -> set:
        """Every bare name used in an expression (or a list of them)."""
        if isinstance(node, list):
            return set().union(*(cls._names_in(item) for item in node)) if node else set()
        if isinstance(node, IdentifierExpr):
            return {node.name}
        if not is_dataclass(node) or isinstance(node, type):
            return set()
        return set().union(*(cls._names_in(getattr(node, f.name)) for f in dataclass_fields(node)
                             if f.name not in ('location', 'inferred_type', 'scope')))

    def attach_methods(self, struct: StructDecl, methods: list) -> None:
        """Methods written inside a struct (Task 32.1): each becomes a function `Struct.name`
        whose first parameter is `this` - the struct itself, by reference, so a method can
        change it. Inside, a field's bare name means `this.field`, and another method's bare
        name `this.method(...)`; a parameter or local can't take a field's name."""
        field_names = {f.name for f in struct.fields}
        method_names = {m.name for m in methods}
        for method in methods:
            clash = next((n for n in method_names if n in field_names), None)
            if clash:
                raise ParserError(self.previous(), f"'{clash}' is both a field and a method of "
                                                   f"struct '{struct.name}'")
            self.rewrite_method_body(method, struct.name, field_names, method_names,
                                     lambda message: self._fail(message))
            method.method_name = method.name
            method.method_of = struct.name
            method.name = f'{struct.name}.{method.name}'
            this = ParameterDecl(location=method.location, name='this', default_value=None,
                                 param_type=StructType(location=method.location, name=struct.name),
                                 by_ref=True)
            method.parameters.insert(0, this)
        changes = {m.method_name: self.assigns_this(m) for m in methods}
        while True:          # a method that calls one that changes `this` changes it too
            more = {m.method_name for m in methods if not changes[m.method_name]
                    and any(changes[n] for n in self.this_calls(m))}
            if not more:
                break
            for name in more:
                changes[name] = True
        for method in methods:
            method.changes_this = changes[method.method_name]
        struct.methods = methods

    def _fail(self, message: str):
        raise ParserError(self.previous(), message)

    @staticmethod
    def rewrite_method_body(method, struct_name, field_names, method_names, fail) -> None:
        """A field's bare name in a method becomes `this.field`, another method's bare call
        `this.method(...)`. Also used for the fields a struct builds on (Task 32.8), which
        are known only once every struct is parsed. `fail(message)` reports a name clash."""
        for p in method.parameters:
            if p.name in field_names or (p.name == 'this' and not getattr(p, 'by_ref', False)):
                fail(f"Parameter '{p.name}' of method '{method.name}' has the name of a field "
                     f"of struct '{struct_name}' - choose another")

        def this_of(node, name):
            return MemberExpr(location=node.location,
                              object=IdentifierExpr(location=node.location, name='this'),
                              member=name)

        def walk(node):
            if isinstance(node, list):
                for i, item in enumerate(node):
                    node[i] = fix(item)
                    walk(node[i])
                return
            if not is_dataclass(node) or isinstance(node, type):
                return
            if isinstance(node, VarDeclStmt) and node.name in field_names:
                fail(f"A variable in method '{method.name}' can't have the name of field "
                     f"'{node.name}'")
            for f in dataclass_fields(node):
                if f.name in ('location', 'inferred_type', 'scope', 'declaration',
                              'callee_declaration', 'resolved_arguments'):
                    continue
                value = getattr(node, f.name)
                if isinstance(value, list):
                    walk(value)
                    continue
                new = fix(value)
                if new is not value:
                    setattr(node, f.name, new)
                walk(new)

        def fix(node):
            if isinstance(node, IdentifierExpr) and node.name in field_names:
                return this_of(node, node.name)
            if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                    and node.callee.name in method_names:
                node.callee = this_of(node.callee, node.callee.name)
            return node

        walk(method.body)

    @staticmethod
    def _root_name(node):
        while isinstance(node, (MemberExpr, IndexExpr)):
            node = node.object if isinstance(node, MemberExpr) else node.array
        return node.name if isinstance(node, IdentifierExpr) else None

    @classmethod
    def assigns_this(cls, method) -> bool:
        """Whether a method changes `this` itself (not counting other methods it calls)."""
        changing = ('add', 'insert', 'removeAt', 'remove', 'clear', 'sort', 'sortBy')
        found = [False]

        def walk(node):
            if found[0] or isinstance(node, type):
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not is_dataclass(node):
                return
            if isinstance(node, AssignmentStmt) and cls._root_name(node.target) == 'this':
                found[0] = True
                return
            if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                    and node.callee.member in changing \
                    and isinstance(node.callee.object, (MemberExpr, IndexExpr)) \
                    and cls._root_name(node.callee.object) == 'this':
                found[0] = True
                return
            for f in dataclass_fields(node):
                if f.name not in ('location', 'inferred_type', 'scope'):
                    walk(getattr(node, f.name))

        walk(method.body)
        return found[0]

    @staticmethod
    def this_calls(method) -> set:
        """The struct's methods a method calls on `this`."""
        names = set()

        def walk(node):
            if isinstance(node, type):
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not is_dataclass(node):
                return
            if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                    and isinstance(node.callee.object, IdentifierExpr) \
                    and node.callee.object.name == 'this':
                names.add(node.callee.member)
            for f in dataclass_fields(node):
                if f.name not in ('location', 'inferred_type', 'scope'):
                    walk(getattr(node, f.name))

        walk(method.body)
        return names

    @classmethod
    def place_at(cls, node, location) -> None:
        """Give a name parsed from inside a string's {...} the string's own position - its
        own lexer starts at line 1, so errors pointed at 1:1 (Task 29.3)."""
        if isinstance(node, ASTNode):
            node.location = location
            for value in vars(node).values():
                if isinstance(value, ASTNode):
                    cls.place_at(value, location)

    def is_template_start(self) -> bool:
        """`template string greet = ...` - `template` is only special before a type and a
        name, so it still works as a variable name (and stays free for other uses later)."""
        return (self.check(TokenType.IDENTIFIER) and self.peek().value == 'template'
                and self.peek(1).type == TokenType.STRING
                and self.peek(2).type == TokenType.IDENTIFIER)

    def parse_template_declaration(self) -> TemplateDecl:
        """`template string greet = "Hello {@1}, you are {@2}"` (Task 29.3): the text must be
        written in the source - it is the body of the function the template becomes."""
        location = self.advance().location          # `template`
        self.advance()                              # `string`
        name_token = self.consume(TokenType.IDENTIFIER, "Expected the template's name")
        self.consume(TokenType.ASSIGN, "Expected '=' and the template's text")
        text = self.parse_expression()
        if not (isinstance(text, InterpolatedStringExpr)
                or (isinstance(text, LiteralExpr) and text.type_hint == 'string')):
            raise ParserError(name_token, "A template's text must be a string written in the "
                                          "source: template string greet = \"Hello {@1}\"")
        self.consume_statement_terminator()
        return TemplateDecl(location=location, name=name_token.value, text=text)

    def is_error_declaration_start(self) -> bool:
        """`error FileError` - not `error function f()` or a variable called error."""
        return (self.check(TokenType.IDENTIFIER) and self.peek().value == 'error'
                and self.peek(1).type == TokenType.IDENTIFIER
                and self.peek(2).type != TokenType.FUNCTION)

    def parse_error_declaration(self) -> ErrorDecl:
        """A custom error type (Task 26.9), in any block style, or just `error Timeout`:

            error FileNotFound : FileError
                message = "File not found"     a default message (and/or `code = 404`)
                bool wasDeleted                its own fields, like a struct's
        """
        error_token = self.advance()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected the error type's name")
        decl = ErrorDecl(location=error_token.location, name=name_token.value)
        if self.match(TokenType.COLON):
            parent = self.consume(TokenType.IDENTIFIER, "Expected the parent error type after ':'")
            decl.parent = parent.value
            while self.check(TokenType.DOT) and self.peek(1).type == TokenType.IDENTIFIER:
                self.advance()
                decl.parent += '.' + self.advance().value     # files.FileError
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.LBRACE):
            closing = TokenType.RBRACE
        elif self.match(TokenType.INDENT):
            closing = TokenType.DEDENT
        else:
            return decl                                     # `error Timeout` - no body
        while True:
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(closing) or self.is_at_end():
                break
            if self.check(TokenType.IDENTIFIER) and self.peek().value in ('message', 'code') \
                    and self.peek(1).type == TokenType.ASSIGN:
                which = self.advance().value
                self.advance()
                value = self.parse_expression()
                self.reject_compare_with_single_equals()   # Task 27.2
                if which == 'message':
                    decl.default_message = value
                else:
                    decl.default_code = value
                continue
            decl.fields.append(self.parse_struct_field())
        self.consume(closing, f"Expected the end of error type '{decl.name}'")
        while self.match(TokenType.NEWLINE):
            pass
        if self.check(TokenType.END) and self.peek(1).value == 'error':
            self.advance()
            self.advance()
        return decl

    def parse_enum_declaration(self) -> EnumDecl:
        """Parse an enum (Task 25), on one line or in any of the three block styles:

            enum Color: Red Green Blue      enum Status          enum Token {
                                                OK = 200             Number(int value)
                                                NotFound = 404       Plus
                                                                 }

        Commas between values are optional (user decision: they are redundant). A value is
        a name, optionally `= <integer>` (default: the previous value + 1, starting at 0),
        or a name with the data it carries in parentheses. `End enum` may close a block.
        The ENUM token has already been consumed.
        """
        enum_token = self.previous()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected the enum's name after 'enum'")
        name = name_token.value

        if self.match(TokenType.COLON):
            closing = TokenType.NEWLINE          # one line: enum Color: Red Green Blue
        else:
            while self.match(TokenType.NEWLINE):
                pass
            if self.match(TokenType.LBRACE):
                closing = TokenType.RBRACE
            elif self.match(TokenType.INDENT):
                closing = TokenType.DEDENT
            else:
                raise ParserError(
                    self.peek(),
                    f"Expected the values of enum '{name}' - after ':' on the same line, an "
                    f"indented block, or '{{' ... '}}'")

        variants = []
        next_value = 0
        while True:
            if closing != TokenType.NEWLINE:
                while self.match(TokenType.NEWLINE):
                    pass
            if self.check(closing) or self.is_at_end():
                break
            if self.match(TokenType.COMMA):
                continue
            variant = self.parse_enum_variant(name, next_value)
            next_value = variant.value + 1
            variants.append(variant)

        if not self.is_at_end():
            self.consume(closing, f"Expected end of enum '{name}'")
        while self.match(TokenType.NEWLINE):
            pass
        # Optional `End enum` (End keyword style)
        if closing != TokenType.NEWLINE and self.check(TokenType.END) \
                and self.peek(1).type == TokenType.ENUM:
            self.advance()
            self.advance()
        if not variants:
            raise ParserError(name_token, f"Enum '{name}' has no values - it needs at least one")
        return EnumDecl(location=enum_token.location, name=name, variants=variants)

    def parse_enum_variant(self, enum_name: str, default_value: int) -> EnumVariant:
        """One enum value: `Red`, `OK = 200`, `Low = -1`, or `Number(int value)` (Task 25)."""
        if not self.check(TokenType.IDENTIFIER):
            raise ParserError(self.peek(), f"Expected a value name in enum '{enum_name}'")
        name_token = self.advance()
        variant = EnumVariant(location=name_token.location, name=name_token.value,
                              value=default_value)
        if self.match(TokenType.LPAREN):
            while not self.check(TokenType.RPAREN) and not self.is_at_end():
                variant.fields.append(self.parse_struct_field())
                if not self.match(TokenType.COMMA):
                    break
            self.consume(TokenType.RPAREN, f"Expected ')' after the data of '{name_token.value}'")
        if self.match(TokenType.ASSIGN):
            negative = self.match(TokenType.MINUS)
            value_token = self.consume(
                TokenType.INTEGER,
                f"The value of '{name_token.value}' must be a whole number, e.g. {name_token.value} = 200")
            variant.value = -integer_value(value_token.value) if negative else integer_value(value_token.value)
            variant.explicit_value = True
        return variant

    def parse_struct_field(self):
        """Parse one struct field: `int x` or `int hp = 100` (Task 18.2.1) - or a method,
        `void function move(int dx)` (Task 32.1), returned as a FunctionDecl. `byRef
        List<string> log` - shared when the struct is copied (Task 32.10a)."""
        passing = self._passing_word()
        if passing is not None:
            self.advance()
        field_type = self.parse_type()
        if self.match(TokenType.FUNCTION, TokenType.FUNC):
            return self.parse_function_declaration(field_type)
        if self.check_any(TokenType.FUNCTION, TokenType.FUNC):
            raise ParserError(
                self.peek(),
                "Structs can only contain fields - structs are pure value types with no "
                "functions (write a separate function that takes the struct instead)"
            )
        name_token = self.consume(TokenType.IDENTIFIER, "Expected field name")
        if self.check(TokenType.LPAREN):
            raise ParserError(
                self.peek(),
                "Structs can only contain fields - structs are pure value types with no "
                "functions (write a separate function that takes the struct instead)"
            )
        default_value = None
        if self.match(TokenType.ASSIGN):
            default_value = self.parse_expression()
        return StructField(
            location=name_token.location,
            by_ref=passing is False,
            field_type=field_type,
            name=name_token.value,
            default_value=default_value
        )

    def parse_function_declaration(self, return_type: TypeNode) -> ASTNode:
        """Parse function declaration: int function add(int a, int b) { body }

        Args:
            return_type: Already-parsed return type

        Returns:
            FunctionDecl AST node
        """
        func_token = self.previous()  # FUNCTION token

        # Function name (allow type keywords as function names)
        # This allows functions named "double", "string", "int", etc.
        if self.check(TokenType.IDENTIFIER) or self.is_type_start():
            name_token = self.advance()
            name = name_token.value
            location = name_token.location
        else:
            raise ParserError(self.peek(), "Expected function name")

        # Parameter list
        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                parameters.append(self.parse_parameter())

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        # Skip newlines after parameter list
        while self.match(TokenType.NEWLINE):
            pass

        # Function body: block or inline lambda
        is_lambda = False
        body = None

        if self.match(TokenType.COLON):
            # Inline lambda: int function add(int a, int b) : a + b
            is_lambda = True

            # Skip newlines after colon
            while self.match(TokenType.NEWLINE):
                pass

            # Check if single expression or multi-line block
            if self.check(TokenType.INDENT):
                # Multi-line lambda with indentation
                body = self.parse_block_statement()
            else:
                # Single expression
                expr = self.parse_expression()
                self.consume_statement_terminator()
                # Wrap in return statement for consistency
                body = BlockStmt(
                    location=expr.location,
                    statements=[ReturnStmt(location=expr.location, value=expr)]
                )

        else:
            # Regular function with block body
            body = self.parse_block_statement()

        # Check for End function (if using End keyword style)
        if self.match(TokenType.END):
            self.consume(TokenType.FUNCTION, "Expected 'function' after 'End'")

        return FunctionDecl(
            location=location,
            return_type=return_type,
            name=name,
            parameters=parameters,
            body=body,
            is_lambda=is_lambda
        )
