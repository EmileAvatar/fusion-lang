"""
Recursive Descent Parser for Fusion Programming Language

This module implements a parser that converts a token stream into an Abstract
Syntax Tree (AST). Uses precedence climbing for binary operators.
"""

import copy
import json
import re
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import List, Optional
from src.lexer.token import Token, TokenType, SourceLocation
from src.lexer.literals import decode_char_literal, integer_value
from src.parser.ast_nodes import *

# `byVal a` / `byValue a` - a copy; `byRef a` - shared (Task 32.10a; words, not keywords)
PASSING_WORDS = {'byVal': True, 'byValue': True, 'byRef': False}



# Fusion's own generic interfaces (Task 32.4): Iterator<T>, Collection<T>
GENERIC_INTERFACE_NAMES = ('Iterator', 'Collection', 'Entry')   # Entry<K, V>: a Map's (32.6)


def type_text(t) -> str:
    """A type as written - `Person`, `int`, `List<int>` - the name of a generic interface's
    element type (`Collection<List<int>>`)."""
    name = getattr(t, 'name', None)
    if type(t).__name__ == 'ListType' and getattr(t, 'growable', False):
        return f'{type_text(t.element_type)}:[]'         # a growable array (Task 45.3)
    if type(t).__name__ == 'ListType' and getattr(t, 'array_form', False):
        return f'{type_text(t.element_type)}[]'          # a heap array (Task 45.10)
    if type(t).__name__ == 'ListType':
        return f'List<{type_text(t.element_type)}>'
    if type(t).__name__ == 'MapType':
        return f'Map<{type_text(t.key_type)}, {type_text(t.value_type)}>'
    if type(t).__name__ == 'ArrayType':
        return f'{type_text(t.element_type)}[]'
    return name or type(t).__name__

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
        self.generic_interfaces = []   # Iterator<Person>, Collection<int> ... (Task 32.4)
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

    def _nesting(self) -> int:
        """How many ( and [ are open at this point - a comma inside them separates values."""
        depth = 0
        for token in self.tokens[:self.current]:
            if token.type in (TokenType.LPAREN, TokenType.LBRACKET, TokenType.LBRACE):
                depth += 1
            elif token.type in (TokenType.RPAREN, TokenType.RBRACKET, TokenType.RBRACE):
                depth -= 1
        return depth

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
        condition = self.parse_coalesce()
        if not self.check(TokenType.QUESTION):
            return condition
        question = self.advance()
        then_value = self.parse_conditional()
        self.consume(TokenType.COLON, "Expected ':' between the two values of '? :' - "
                                      "(condition) ? a : b")
        else_value = self.parse_conditional()
        return ConditionalExpr(location=question.location, condition=condition,
                               then_value=then_value, else_value=else_value)

    def parse_coalesce(self) -> ASTNode:
        """`a ?? b` - a, or b when a is missing (Task 52.8); groups to the right."""
        left = self.parse_or()
        if self.check(TokenType.NULL_COALESCE):
            operator = self.advance()
            return CoalesceExpr(location=operator.location, left=left, right=self.parse_coalesce())
        return left

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

        # x is null / x is not null (Task 30.11); x is Circle / x is not Shape (Task 32.5a)
        if self.check(TokenType.IS):
            self.advance()
            negated = self.match(TokenType.NOT)
            if self.match(TokenType.NULL):
                expr = IsNullExpr(location=expr.location, operand=expr, negated=negated)
            elif self.is_type_start() or self.check(TokenType.IDENTIFIER):
                expr = IsTypeExpr(location=expr.location, operand=expr, target=self.parse_type(),
                                  negated=negated)
            else:
                raise ParserError(self.peek(), "Expected 'null' or a type after 'is'")

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

        # `(Shape)aCircle` - a cast written in front (Task 32.5a, D.082): `( Name )` followed by
        # a value - a name, `this`, `new` or `(` - never `(a) + b` or `(c) ? x : y`
        if self.check(TokenType.LPAREN) and self.peek(2).type == TokenType.RPAREN and (
                self.peek(1).type == TokenType.IDENTIFIER or self.peek(1).type in self.PRIMITIVE_TYPE_TOKENS) \
                and self.peek(3).type in (TokenType.IDENTIFIER, TokenType.THIS, TokenType.NEW,
                                          TokenType.LPAREN):
            start = self.advance()
            target = self.parse_type()
            self.consume(TokenType.RPAREN, "Expected ')' after the type of a cast")
            return CastExpr(location=start.location, target=target, operand=self.parse_unary())

        # `byVal a` (or byValue) - a copy; `byRef a` - shared (Task 32.10a). Words only here
        passing = self._passing_word()
        if passing is not None:
            word = self.advance()
            return PassingExpr(location=word.location, value=self.parse_unary(),
                               by_val=passing)
        # `f(readonly acc)` - the caller's demand: this call doesn't change acc (Task 48.3)
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'readonly' \
                and self.peek(1).type in (TokenType.IDENTIFIER, TokenType.LPAREN):
            word = self.advance()
            return PassingExpr(location=word.location, value=self.parse_unary(),
                               by_val=False, is_readonly=True)

        return self.parse_call()

    def _passing_word(self):
        """True for `byVal` / `byValue`, False for `byRef`, before a value or a type; None
        when the word is just a name."""
        if not self.check(TokenType.IDENTIFIER) or self.peek().value not in PASSING_WORDS:
            return None
        if self.peek(1).type not in (TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LBRACKET,
                                     TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                                     TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
                                     TokenType.BYTE, TokenType.SHORT, TokenType.LONG, TokenType.INT128, TokenType.INT256):
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
        type_args = None
        while True:
            if isinstance(expr, IdentifierExpr) and type_args is None and self.check(TokenType.LESS) \
                    and self._type_arguments_ahead():
                type_args = self._type_arguments()     # first<int>(numbers) (Task 33, D.166)
                continue
            if self.check(TokenType.SAFE_NAV):
                # x?.null - quick typing for "x is null" (Task 30.11)
                if self.peek(1).type == TokenType.NULL:
                    self.advance(); self.advance()
                    expr = IsNullExpr(location=expr.location, operand=expr)
                    continue
                # x?.name / x?.f() - the null guard (Task 52.8)
                self.advance()
                name = self.peek()
                if name.type != TokenType.IDENTIFIER and not name.value.isidentifier():
                    raise ParserError(name, "Expected a field or method name after '?.'")
                self.advance()
                expr = MemberExpr(location=expr.location, object=expr, member=name.value, guarded=True)
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
                if type_args is not None:
                    expr.type_args, type_args = type_args, None
            elif isinstance(expr, IndexExpr) and self.check(TokenType.COMMA) \
                    and self.peek(1).type == TokenType.LBRACKET and self._nesting() == 0:
                self.advance()       # m[1],[2] - the same slot as m[1][2] (D.143); not inside ( ) or [ ]
            elif self.match(TokenType.LBRACKET):
                # cube[][2] - an index left out: all of that dimension (a view - 45.12b, D.149)
                index = None if self.check(TokenType.RBRACKET) else self.parse_expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after array index")

                expr = IndexExpr(
                    location=expr.location,
                    array=expr,
                    index=index
                )
            elif self.match(TokenType.DOT):
                if type_args is not None and isinstance(expr, IdentifierExpr):
                    expr.type_args, type_args = type_args, None      # Box<int>.made (33.3c)
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
        # `::total` - the module's variable, where a local of that name hides it (47.12, D.200)
        if self.check(TokenType.COLON) and self.peek(1).type == TokenType.COLON \
                and self.peek(2).type == TokenType.IDENTIFIER:
            start = self.advance()
            self.advance()
            name = self.advance()
            expr = IdentifierExpr(location=start.location, name=name.value)
            expr.module_scope = True
            return expr
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
            from src.lexer.literals import split_number
            whole, places, exponent, suffix = split_number(token.value)
            text = f"{whole or '0'}.{places or '0'}e{exponent}"
            value = float(text)
            if value in (float('inf'), float('-inf')):
                raise ParserError(token, f"{token.value} is past a double's range (about 1.8e308) - never infinity; "
                                         f"Double.INFINITY names it")
            if value == 0.0 and int((whole or '0') + places) != 0:
                raise ParserError(token, f"{token.value} is too small for a double (about 4.9e-324) - it would be 0")
            # the smallest type that holds it (D.196): a float, unless past a float's range - then a double
            hint = 'double' if suffix in ('d', 'D') or (abs(value) > 3.4028234663852886e38 and suffix not in ('f', 'F')) \
                else 'float'
            if suffix in ('f', 'F') and abs(value) > 3.4028234663852886e38:
                raise ParserError(token, f"{token.value} is past a float's range (about 3.4e38) - drop the f for a double")
            literal = LiteralExpr(location=token.location, value=value, type_hint=hint)
            literal.written = token.value.replace('_', '')   # its digits as written - a decimal keeps them (47.8)
            literal.suffix = suffix if suffix in ('m', 'dec') else None     # 19.99m, 0.155dec (47.9d)
            return literal

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

        # Entry<string, int>("a", 1) - a Map's entry, made (Task 32.6)
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'Entry' \
                and self.peek(1).type == TokenType.LESS:
            token = self.advance()
            kind = self._generic_interface_type(token, 'Entry')
            return IdentifierExpr(location=token.location, name=kind.name)

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
        param_type = self._brackets_after_name(param_type, name)

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
        arrays (`int[][]`) are not yet supported either - see files/taskSummary2.md Task 9.

        Returns:
            TypeNode (PrimitiveType, or ArrayType wrapping one, for MVP)
        """
        # `fixed(10) string`, `fixed(14) List<Person>` - at most n (Task 47.5, D.020, D.064)
        if self.check(TokenType.FIXED) and self.peek(1).type == TokenType.LPAREN:
            fixed_token = self.advance()
            self.advance()
            if self.check(TokenType.INTEGER):
                size = integer_value(self.advance().value)
            elif self.check(TokenType.IDENTIFIER):
                size = self.advance().value              # a const's name - worked out with the program
            else:
                raise ParserError(self.peek(), "fixed(n) takes a whole number or a constant's name: fixed(10) string")
            self.consume(TokenType.RPAREN, "Expected ')' after the size in fixed(n)")
            inner = self.parse_type()
            if not (isinstance(inner, (ListType, MapType)) or (isinstance(inner, PrimitiveType)
                                                               and inner.name == 'string')):
                raise ParserError(fixed_token, "fixed(n) goes on a string, a List or a Map - an array that never "
                                               "changes size is written fixed int[10] c")
            inner.fixed_max = size
            inner.fixed_location = fixed_token.location
            return inner

        # Function type (Task 18.1.3): (int, int) : int  or  (int, int) -> int
        if self.check(TokenType.LPAREN):
            return self.parse_function_type()

        # Otherwise a primitive type or a struct name (optionally as an array)
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                      TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
                      TokenType.VOID, TokenType.BYTE, TokenType.SHORT, TokenType.LONG, TokenType.INT128, TokenType.INT256):
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
            elif name in GENERIC_INTERFACE_NAMES and self.check(TokenType.LESS):
                base_type = self._generic_interface_type(token, name)      # Task 32.4
            elif name in ('bytes', 'decimal', 'money'):
                # Raw bytes (Task 18.3.8), an exact decimal (47.8), money (47.2) - built-in types, not keywords
                base_type = PrimitiveType(location=token.location, name=name)
            elif self.check(TokenType.LESS):
                # Pair<int, string> - a generic struct with its types (Task 33.2b, D.166)
                args = self._type_arguments()
                base_type = StructType(location=token.location,
                                       name=f'{name}<{", ".join(type_text(a) for a in args)}>')
                base_type.type_args = args
                base_type.generic_base = name
            else:
                base_type = StructType(location=token.location, name=name)
        else:
            base_type = None

        if base_type is not None:
            growable = self._growable_brackets(base_type)
            if growable is not None:
                return growable
            if self.check(TokenType.LBRACKET):
                return self._array_of(base_type, self._read_dims('int[5]'))

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
        # List<int> xs, Map<string, int> ages (Task 18.5); Collection<int> c (Task 32.4)
        # ... and Pair<int, string> p - a generic struct (Task 33.2b): a name must follow the '>'
        if self.peek(1).type == TokenType.LESS:
            offset = self._skip_type_arguments(1)
            if offset < 0:
                return False
        # money.Price p - a struct from another module (Task 18.4.2)
        while self.peek(offset).type == TokenType.DOT and self.peek(offset + 1).type == TokenType.IDENTIFIER:
            offset += 2
        # Car:[2][3] cars, Car[[2],[3]] cars - a growable array of many dimensions (45.12d)
        growable_start = (self.peek(offset).type == TokenType.COLON and self.peek(offset + 1).type == TokenType.LBRACKET) \
            or (self.peek(offset).type == TokenType.LBRACKET and self.peek(offset + 1).type == TokenType.LBRACKET)
        if growable_start:
            skip = offset
            while self.peek(skip).type in (TokenType.COLON, TokenType.LBRACKET, TokenType.RBRACKET,
                                           TokenType.INTEGER, TokenType.COMMA):
                skip += 1
            if self.peek(skip).type == TokenType.IDENTIFIER and skip - offset > 4:
                return True
        # Car:[] cars, Car[[]] cars - a growable array (Task 45.3); Car:[2], Car[[2]] (45.3b)
        kinds = [self.peek(offset + i).type for i in range(5)]
        if kinds[2] == TokenType.INTEGER:
            del kinds[2]                               # the size made ahead
            sized = 1
        else:
            sized = 0
        if kinds[:3] == [TokenType.COLON, TokenType.LBRACKET, TokenType.RBRACKET]:
            offset += 3 + sized
        elif kinds[:4] == [TokenType.LBRACKET, TokenType.LBRACKET, TokenType.RBRACKET, TokenType.RBRACKET]:
            offset += 4 + sized
        elif self.peek(offset).type == TokenType.LBRACKET:
            while self.peek(offset).type == TokenType.LBRACKET:      # Car[2][3] - 45.12
                offset += 1
                if self.peek(offset).type == TokenType.INTEGER:
                    offset += 1
                if self.peek(offset).type != TokenType.RBRACKET:
                    return False
                offset += 1
                if self.peek(offset).type == TokenType.COMMA and self.peek(offset + 1).type == TokenType.LBRACKET:
                    offset += 1                        # Car[2],[3] cars
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
            elif kind == TokenType.FIXED and self.peek(offset + 1).type == TokenType.LPAREN \
                    and self.peek(offset + 3).type == TokenType.RPAREN:
                offset += 4                              # Map<int, fixed(15) string> (47.5)
                continue
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
        than splitting text and expressions into two parallel arrays - see files/taskSummary2.md
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
        # `outer: for ...` - a loop's label (Task 56.3, D.219)
        if self.check(TokenType.IDENTIFIER) and self.peek(1).type == TokenType.COLON \
                and self.peek(2).type in (TokenType.FOR, TokenType.WHILE):
            label = self.advance().value
            self.advance()
            loop = self.parse_statement()
            loop.label = label
            return loop

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
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'foreach' and self._is_foreach():
            return self.parse_foreach_statement()                      # Task 32.4

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

        # `fixed int[10] c` - an array that never changes size (Task 45.14, D.141)
        if self.check(TokenType.FIXED):
            return self.parse_fixed_declaration()

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

    def _growable_brackets(self, base_type: TypeNode, name: str = None):
        """`int:[]` / `int[[]]` - a growable array (Task 45.3, D.141): on the heap, it grows and
        shrinks at its end. None when the brackets that follow aren't one."""
        colon = self.check(TokenType.COLON) and self.peek(1).type == TokenType.LBRACKET
        double = self.check(TokenType.LBRACKET) and self.peek(1).type == TokenType.LBRACKET
        if not (colon or double):
            return None
        start = self.advance()
        self.advance()

        def one_size():
            size = None
            if self.check(TokenType.INTEGER):      # int:[10] - 10 slots made ahead (45.3b, D.141)
                size = integer_value(self.advance().value)
            elif not self.check(TokenType.RBRACKET):
                raise ParserError(self.peek(), "A growable array's size is a whole number written in the source - "
                                               "int:[10] numbers - or none: int:[] numbers")
            self.consume(TokenType.RBRACKET, "Expected ']' - a growable array is written int:[] or int:[10]")
            return size

        dims = [one_size()]
        if double:
            while self.check(TokenType.COMMA) and self.peek(1).type == TokenType.LBRACKET:
                self.advance()
                self.advance()
                dims.append(one_size())           # int[[2],[3],[4]] - many dimensions (45.12d)
            self.consume(TokenType.RBRACKET, "Expected ']]' - a growable array is written int[[]] or int[[10]]")
        else:
            while self.check(TokenType.LBRACKET) or (self.check(TokenType.COMMA)
                                                     and self.peek(1).type == TokenType.LBRACKET):
                if self.match(TokenType.COMMA):
                    pass                          # int:[2],[3] - the same as int:[2][3]
                self.advance()
                dims.append(one_size())           # int:[2][3][4] (45.12d)
        if len(dims) > 1:
            grid = self._array_of(base_type, dims)
            grid.size = None                      # its sizes change while running (expand)
            grid.growable = True
            return grid
        return ListType(location=base_type.location, element_type=base_type, array_form=True,
                        growable=True, start_size=dims[0])

    def _read_dims(self, example: str) -> list:
        """`[2][3][4]` or `[2],[3],[4]` - one size per dimension (None when not written). The
        commas only break it up (D.143)."""
        dims = []
        while self.match(TokenType.LBRACKET):
            size = None
            if not self.check(TokenType.RBRACKET):
                size_token = self.consume(TokenType.INTEGER, f"Array size must be an integer literal, e.g. {example}")
                size = integer_value(size_token.value)
            self.consume(TokenType.RBRACKET, "Expected ']' after array size")
            dims.append(size)
            if self.check(TokenType.COMMA) and self.peek(1).type == TokenType.LBRACKET:
                self.advance()                    # int[2],[3] - the same as int[2][3]
        return dims

    def _array_of(self, element: TypeNode, dims: list) -> TypeNode:
        """The array type for these sizes - up to 3 dimensions in the core (D.143)."""
        if len(dims) > 3:
            raise ParserError(self.previous(), f"An array of {len(dims)} dimensions - more than 3 come with the "
                                               f"Collections library (later); the core has up to 3 (D.143)")
        if len(dims) == 1:
            return ArrayType(location=element.location, element_type=element, size=dims[0])
        if None in dims and any(d is not None for d in dims):
            raise ParserError(self.previous(), "Give every size or none: int[2][3] m, or int[][] m = [[...], [...]]")
        if 0 in dims:
            raise ParserError(self.previous(), "A dimension of size 0 - each size of a many-dimension array is "
                                               "1 or more")
        size = None
        if None not in dims:
            size = 1
            for d in dims:
                size *= d
        return ArrayType(location=element.location, element_type=element, size=size, dims=dims)

    def _brackets_after_name(self, var_type: TypeNode, name: str) -> TypeNode:
        """C-style `int numbers[]` / `int numbers[10]` - the same array as `int[] numbers` /
        `int[10] numbers`, written the other way (user, 2026-11-15 - both kept, a preference)."""
        if self.check(TokenType.LBRACKET) and self.peek(1).type == TokenType.LBRACKET \
                and not isinstance(var_type, (ArrayType, ListType)):
            return self._growable_brackets(var_type, name)          # int numbers[[]] (45.3)
        if not self.check(TokenType.LBRACKET):
            return var_type
        if isinstance(var_type, ArrayType):
            raise ParserError(self.peek(), f"Write the brackets once: {self.type_text(var_type)} {name}, "
                                           f"or {self.type_text(var_type.element_type)} {name}[]")
        return self._array_of(var_type, self._read_dims(f'{name}[5]'))

    @staticmethod
    def type_text(type_node) -> str:
        if isinstance(type_node, ArrayType) and type_node.dims:
            return Parser.type_text(type_node.element_type) + ''.join(
                f"[{'' if d is None else d}]" for d in type_node.dims)
        if isinstance(type_node, ArrayType):
            size = '' if type_node.size is None else str(type_node.size)
            return f"{Parser.type_text(type_node.element_type)}[{size}]"
        return getattr(type_node, 'name', 'T')

    def parse_fixed_declaration(self) -> ASTNode:
        """`fixed int[10] c`, `fixed int[] d = [5, 2, 3]` (Task 45.14, D.141): an array whose size
        is set once, when it is made. `fixed(n)` - at most n - on strings, Lists and Maps is Task 47.5."""
        if self.peek(1).type == TokenType.LPAREN:         # fixed(10) string name - at most n (47.5)
            return self.parse_var_declaration()
        fixed_token = self.consume(TokenType.FIXED, "Expected 'fixed'")
        if not (self.is_type_start() or self.is_struct_type_declaration_start()):
            raise ParserError(self.peek(), "After 'fixed' comes an array type: fixed int[10] c")
        declaration = self.parse_var_declaration()
        if getattr(declaration.var_type, 'growable', False):
            raise ParserError(fixed_token, "fixed and a growable array can't go together - fixed int[10] "
                                           "never changes size, int:[] grows (D.141)")
        if not isinstance(declaration.var_type, ArrayType):
            raise ParserError(fixed_token, "fixed is written on an array - fixed int[10] c; on a string, List or "
                                           "Map it takes a size: fixed(10) string name")
        declaration.is_fixed = True
        declaration.location = fixed_token.location
        return declaration

    def parse_var_declaration(self) -> ASTNode:
        """Parse variable declaration: int x = 5

        Returns:
            VarDeclStmt AST node
        """
        var_type = self.parse_type()

        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        location = name_token.location
        var_type = self._brackets_after_name(var_type, name)

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
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'readonly' \
                and self.peek(1).type not in (TokenType.NEWLINE, TokenType.DOT, TokenType.LPAREN,
                                              TokenType.LBRACKET):
            raise ParserError(self.peek(), "readonly goes in the signature, not the return - "
                                           "`readonly Engine function getEngine()` (D.110)")
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
        label = self.advance().value if self.check(TokenType.IDENTIFIER) else None   # `break outer` (56.3)
        self.consume_statement_terminator()

        return BreakStmt(
            location=break_token.location,
            label=label
        )

    def parse_continue_statement(self) -> ASTNode:
        """Parse continue statement: continue

        Returns:
            ContinueStmt AST node
        """
        continue_token = self.previous()  # CONTINUE token
        label = self.advance().value if self.check(TokenType.IDENTIFIER) else None   # 56.3
        self.consume_statement_terminator()

        return ContinueStmt(location=continue_token.location, label=label)

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
        pattern = MatchPattern(location=location, value=self.parse_unary())
        if self.check(TokenType.RANGE):              # case 0...9 - both ends included (33.2f, L7.7)
            dots = self.advance()
            pattern.range_end = self.parse_unary()
            first, last = self._written_int(pattern.value), self._written_int(pattern.range_end)
            if first is not None and last is not None and first > last:
                raise ParserError(dots, f"case {first}...{last} - a range goes from the smaller to the larger: "
                                        f"case {last}...{first}")
        return pattern

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

    def _is_foreach(self) -> bool:
        """`foreach (T x in c)` or `foreach x in c` - a word, not a keyword (Task 32.4)."""
        if self.peek(1).type == TokenType.IDENTIFIER and self.peek(2).type == TokenType.IN:
            return True
        if self.peek(1).type != TokenType.LPAREN:
            return False
        depth, i = 0, 1
        while self.current + i < len(self.tokens):
            kind = self.peek(i).type
            if kind == TokenType.LPAREN:
                depth += 1
            elif kind == TokenType.RPAREN:
                depth -= 1
                if depth == 0:
                    return False
            elif kind == TokenType.IN and depth == 1:
                return True
            elif kind in (TokenType.NEWLINE, TokenType.EOF):
                return False
            i += 1
        return False

    @staticmethod
    def _written_int(node):
        """A whole number written in the code (`5`, `-2`), or None."""
        if isinstance(node, LiteralExpr) and node.type_hint == 'int':
            return integer_value(node.value) if isinstance(node.value, str) else node.value
        if isinstance(node, UnaryExpr) and node.operator == '-':
            inner = Parser._written_int(node.operand)
            return None if inner is None else -inner
        return None

    def _range_after(self, start):
        """`for i in 1...10` (Task 33.2f, SYN.034, D.169): both ends included - a range call marked
        `inclusive`. `step` (33.2g, D.170) - a word only here: `0...13 step 5` (0 5 10), a negative step
        counts down (`10...0 step -2`); a written step of 0 is an error, one from a value is checked
        while running. Numbers written against the step's way (`10...1`) are an error."""
        if not self.check(TokenType.RANGE):
            return start
        dots = self.advance()
        end = self.parse_expression()
        step = None
        if self.check(TokenType.IDENTIFIER) and self.peek().value == 'step':
            self.advance()
            step = self.parse_expression()
        first, last = self._written_int(start), self._written_int(end)
        stride = 1 if step is None else self._written_int(step)
        if stride == 0:
            raise ParserError(dots, "A range's step can't be 0 - the loop would never end")
        if first is not None and last is not None and stride is not None:
            if step is None and first > last:
                raise ParserError(dots, f"{first}...{last} counts down - write {first}...{last} step -1 "
                                        f"(or range({first}, {last - 1}, -1))")
            if stride > 0 and first > last:
                raise ParserError(dots, f"{first}...{last} step {stride} never starts - a positive step counts up; "
                                        f"write step -{stride} to count down")
            if stride < 0 and first < last:
                raise ParserError(dots, f"{first}...{last} step {stride} never starts - a negative step counts "
                                        f"down; write step {-stride} to count up")
        arguments = [start, end] + ([step] if step is not None else [])
        call = CallExpr(location=start.location, callee=IdentifierExpr(location=start.location, name='range'),
                        arguments=arguments)
        call.written_range = True
        call.inclusive = True                    # both ends - the C loop compares with <= / >=
        if first is not None and last is not None and stride is not None:
            call.range_numbers = (first, last, stride)      # all written: the step checked on the end
        return call

    def parse_foreach_statement(self) -> ASTNode:
        """`foreach (string n in names)` / `foreach n in names` (Task 32.4, D.049): a loop over
        any collection - an array, List, Map (its keys) or a class implementing
        Collection<T>; the item's written type must be the collection's."""
        start = self.advance()
        declared = None
        parens = self.match(TokenType.LPAREN)
        if parens and not (self.check(TokenType.IDENTIFIER) and self.peek(1).type == TokenType.IN):
            declared = self.parse_type()
        variable = self.consume(TokenType.IDENTIFIER, "Expected the item's name in foreach").value
        self.consume(TokenType.IN, "Expected 'in' after the item in foreach")
        iterable = self._range_after(self.parse_expression())
        if parens:
            self.consume(TokenType.RPAREN, "Expected ')' after the collection in foreach")
        while self.match(TokenType.NEWLINE):
            pass
        body = self.parse_block_statement()
        if self.match(TokenType.END):
            if not self.match(TokenType.FOR):
                self.consume(TokenType.IDENTIFIER, "Expected 'foreach' after 'End'")
        loop = ForStmt(location=start.location, variable=variable, iterable=iterable, body=body)
        loop.is_foreach = True
        loop.declared_type = declared
        return loop

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

        # Iterable expression - or a range `1...10` (Task 33.2f)
        iterable = self._range_after(self.parse_expression())

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

    # The type keywords - a cast `(int)x` starts with one (Task 32.5a)
    PRIMITIVE_TYPE_TOKENS = (TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE, TokenType.STRING,
                             TokenType.BOOL, TokenType.CHAR, TokenType.BYTE, TokenType.SHORT,
                             TokenType.LONG, TokenType.INT128, TokenType.INT256)

    def is_readonly_result_start(self) -> bool:
        """`readonly Engine function ...` - `readonly` before a function's result type (Task 50.1).
        `readonly` is not a reserved word: it counts here only when a type follows it."""
        return self.check(TokenType.IDENTIFIER) and self.peek().value == 'readonly' \
            and self.peek(1).type in (TokenType.IDENTIFIER, TokenType.INT, TokenType.FLOAT,
                                      TokenType.DOUBLE, TokenType.STRING, TokenType.BOOL,
                                      TokenType.CHAR, TokenType.BYTE, TokenType.SHORT,
                                      TokenType.LONG, TokenType.INT128, TokenType.INT256, TokenType.VOID)

    def readonly_result(self, parse) -> 'FunctionDecl':
        """Read `readonly`, then the declaration `parse` reads - it must be a function."""
        word = self.advance()
        decl = parse()
        if not isinstance(decl, FunctionDecl):
            raise ParserError(word, "'readonly' before a type marks a function's result - "
                                    "`readonly Engine function getEngine()`; a variable that "
                                    "never changes is `const`")
        decl.returns_readonly = True
        return decl

    def is_type_start(self) -> bool:
        """Check if current token starts a type.

        Returns:
            True if current token is a type keyword
        """
        return self.check_any(
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
            TokenType.VOID, TokenType.BYTE, TokenType.SHORT, TokenType.LONG, TokenType.INT128, TokenType.INT256
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

        # `namespace Core.Collections` - the first line, before the imports (Task 32.2h)
        namespace = None
        if self.match(TokenType.NAMESPACE):
            parts = [self.consume(TokenType.IDENTIFIER, "Expected a name after 'namespace'").value]
            while self.match(TokenType.DOT):
                parts.append(self.consume(TokenType.IDENTIFIER,
                                          "Expected a name after '.' in the namespace").value)
            if not (self.check(TokenType.NEWLINE) or self.is_at_end()):
                raise ParserError(self.peek(), "Expected the end of the line after the namespace")
            namespace = '.'.join(parts)
            while self.match(TokenType.NEWLINE):
                pass

        # `module Database` - after the namespace line, before the imports (Task 57.1, D.204)
        module = None
        if self.match(TokenType.MODULE):
            module = self.consume(TokenType.IDENTIFIER, "Expected the module's name after 'module'").value
            if self.check(TokenType.DOT):
                raise ParserError(self.peek(), "A module's name is one word - the folders above it are "
                                               "its namespace: write 'namespace A' then 'module B'")
            if not (self.check(TokenType.NEWLINE) or self.is_at_end()):
                raise ParserError(self.peek(), "Expected the end of the line after the module's name")
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
            if self.check(TokenType.NAMESPACE):
                raise ParserError(self.peek(), "'namespace' must be the first line of the file - "
                                               "before the imports")
            if self.check(TokenType.MODULE):
                raise ParserError(self.peek(), "'module' comes right after the namespace line (or "
                                               "first) - before the imports")
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
                # Types and functions are public unless written otherwise; module variables
                # private - their module (Tasks 32.2a, 32.2h)
                if isinstance(decl, (StructDecl, EnumDecl, ErrorDecl, FunctionDecl)) \
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
            imports=imports,
            namespace=namespace,
            module=module
        )

    def parse_import(self) -> ImportDecl:
        """Parse an import line, the IMPORT token already consumed (Task 18.4.2):
        `import money`, `import money.Price`, `import money.*`, `import lib.utils as u`."""
        import_token = self.previous()
        root = None
        if self.match(TokenType.STRING_LIT):          # `import "C:/vendor".SQL.Database` (Task 57.3, D.213)
            parts = json.loads(self.previous().value)
            if len(parts) != 1 or parts[0][0] != 'STRING_PART' or not parts[0][1]:
                raise ParserError(self.previous(), "An import's folder is plain text - no {...} in it")
            root = parts[0][1]
            self.consume(TokenType.DOT, "Expected '.' and the module's name after the folder")
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
        return ImportDecl(location=import_token.location, path=path, star=star, alias=alias, root=root)

    def parse_declaration(self) -> Optional[ASTNode]:
        """Parse top-level declaration (function, var, etc.).

        Returns:
            Declaration AST node or None if no valid declaration found

        Raises:
            ParserError: If declaration is malformed
        """
        # `public` / `internal` / `private` before a top-level item (Tasks 18.4.3, 32.2h)
        if self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.INTERNAL):
            modifier = self.previous()
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(TokenType.PUBLIC) or self.check(TokenType.PRIVATE) \
                    or self.check(TokenType.INTERNAL):
                raise ParserError(self.peek(), "Only one of 'public' / 'internal' / 'private' "
                                               "may be given")
            if not (self.check(TokenType.STRUCT) or self.check(TokenType.ENUM)
                    or self.check(TokenType.CONST) or self.check(TokenType.CLASS)
                    or self.check(TokenType.STATIC)
                    or self.check(TokenType.INTERFACE) or self.check(TokenType.ABSTRACT)
                    or self.check(TokenType.SEALED)
                    or self.is_error_declaration_start() or self.is_type_start()
                    or self.is_function_type_declaration_start()
                    or self.is_struct_type_declaration_start()
                    or self.is_readonly_result_start()):
                raise ParserError(modifier, f"'{modifier.value}' can only come before a struct, "
                                            f"an enum, a function or a module variable")
            decl = self.parse_declaration()
            if not isinstance(decl, (FunctionDecl, StructDecl, EnumDecl, ErrorDecl, VarDeclStmt)):
                raise ParserError(modifier, f"'{modifier.value}' can only come before a struct, "
                                            f"an enum, a function or a module variable")
            # `private` on a top-level type: its module only (D.212 - internal is the namespace);
            # on a function an error - it is public or internal
            if modifier.type == TokenType.PRIVATE and isinstance(decl, FunctionDecl):
                raise ParserError(modifier, "'private' can't be on a top-level function - write "
                                            "'internal' (its namespace), or put it in a class")
            decl.is_private_top = modifier.type == TokenType.PRIVATE and not isinstance(decl, VarDeclStmt)
            decl.is_public = modifier.type == TokenType.PUBLIC
            decl.is_internal = modifier.type == TokenType.INTERNAL
            decl.visibility_written = True
            return decl

        # `readonly Engine function getEngine()` - a readonly result (Task 50.1, D.110)
        if self.is_readonly_result_start():
            return self.readonly_result(self.parse_declaration)

        # A module-level `let` / `var` (Task 46.1)
        if self.check(TokenType.LET) or self.check(TokenType.VAR):
            return self.parse_inferred_declaration()

        # `const static enum Planet` - accepted, changing nothing: an enum is always const and static (47.3)
        if self.check(TokenType.CONST) or self.check(TokenType.STATIC):
            ahead = 0
            while self.peek(ahead).type in (TokenType.CONST, TokenType.STATIC):
                ahead += 1
            if self.peek(ahead).type == TokenType.ENUM:
                for _ in range(ahead + 1):
                    self.advance()
                return self.parse_enum_declaration()

        # `static` at the top of a module (Task 57.2, D.212): a function or variable there is static -
        # written out; an interface is static already
        if self.match(TokenType.STATIC):
            if self.match(TokenType.INTERFACE):
                return self.parse_interface_declaration()
            word = self.previous()
            decl = self.parse_declaration()
            if not isinstance(decl, (FunctionDecl, VarDeclStmt)):
                raise ParserError(word, "'static' at the top of a file comes before a function, a "
                                        "variable, an enum or an interface")
            decl.static_written = True
            return decl

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
        if self.match(TokenType.INTERFACE):
            return self.parse_interface_declaration()
        if self.check(TokenType.ABSTRACT) or self.check(TokenType.SEALED):
            word = self.advance()                      # Task 32.7 (D.084)
            self.consume(TokenType.CLASS, f"'{word.value}' goes before 'class' (or before a "
                                          f"function inside a class)")
            decl = self.parse_class_declaration()
            decl.is_abstract = word.type == TokenType.ABSTRACT
            decl.is_sealed = word.type == TokenType.SEALED
            return decl
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

    def _implements_list(self) -> list:
        """`implements A, B, C` - the IMPLEMENTS token already consumed (Task 32.5a);
        `Collection<Person>` too (Task 32.4)."""
        names = [self._interface_name()]
        while self.match(TokenType.COMMA):
            names.append(self._interface_name())
        return [n for n in names if n is not None]       # List<T>: not an interface of its own (33.3d1)

    def _interface_name(self) -> str:
        token = self.consume(TokenType.IDENTIFIER, "Expected an interface's name after 'implements'")
        if token.value == 'List' and self.check(TokenType.LESS):
            # class Ring<T> implements List<T> (33.3d1, D.174): its own List - the core five written, the rest added
            self.consume(TokenType.LESS, "Expected '<'")
            self.list_element = self.parse_type()
            self.consume(TokenType.GREATER, "Expected '>' after the type in List<...>")
            return None
        if token.value in GENERIC_INTERFACE_NAMES and self.check(TokenType.LESS):
            kind = self._generic_interface_type(token, token.value)
            self.generic_interfaces.append(kind)
            return kind.name
        return token.value

    def _generic_interface_type(self, token, name: str) -> StructType:
        """`Iterator<Person>`, `Collection<int>` (Task 32.4): one of Fusion's own interfaces,
        made for that element type - the name holds it (`Collection<Person>`)."""
        self.consume(TokenType.LESS, "Expected '<'")
        args = [self.parse_type()]
        while name == 'Entry' and self.match(TokenType.COMMA):
            args.append(self.parse_type())
        self.consume(TokenType.GREATER, f"Expected '>' after the type in {name}<...>")
        if name == 'Entry' and len(args) != 2:
            raise ParserError(self.previous(), "Entry has two types - Entry<string, int>")
        kind = StructType(location=token.location, name=f'{name}<{", ".join(type_text(a) for a in args)}>')
        kind.type_args = args
        self.generic_interfaces.append(kind)
        return kind

    def parse_interface_declaration(self) -> StructDecl:
        """`interface Shape` (Task 32.5a, D.087): function signatures only - what, not how.

            interface Shape implements Named, Printable
                float function area()
                float function scale(float k)

        Each signature becomes the function `Shape.area` with `this` first, like a class's
        method; it has no body - semantic analysis turns it into a look-up of the object's own
        function. A body is a default method, allowed only by [interfaces] defaultMethods. The
        INTERFACE token has already been consumed."""
        start = self.previous()
        name = self.consume(TokenType.IDENTIFIER, "Expected the interface's name after 'interface'").value
        parents = self._implements_list() if self.match(TokenType.IMPLEMENTS) else []
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.LBRACE):
            closing = TokenType.RBRACE
        elif self.match(TokenType.INDENT):
            closing = TokenType.DEDENT
        else:
            raise ParserError(self.peek(), f"Expected the functions of interface '{name}' - an "
                                           f"indented block, or '{{' ... '}}'")
        methods = []
        while True:
            while self.match(TokenType.NEWLINE):
                pass
            if self.check(closing) or self.is_at_end():
                break
            if self.check(TokenType.PRIVATE) or self.check(TokenType.PROTECTED):   # 52.6 (D.114)
                raise ParserError(self.peek(), f"An interface's functions are public or internal - "
                                               f"'{self.peek().value}' would hide it from the classes "
                                               f"that implement '{name}'")
            internal = self.match(TokenType.INTERNAL)
            if not internal:
                self.match(TokenType.PUBLIC)        # an interface's functions are public anyway
            readonly = self.is_readonly_result_start()              # Task 50.1 (D.110)
            if readonly:
                self.advance()
            return_type = self.parse_type()
            if not self.match(TokenType.FUNCTION, TokenType.FUNC):
                raise ParserError(self.peek(), f"An interface holds functions only - '{name}' "
                                               f"can't have a field (a class that implements it can)")
            method = self.parse_function_declaration(return_type, signature_only=True)
            method.returns_readonly = readonly
            method.is_internal = internal
            methods.append(method)
        self.consume(closing, f"Expected the end of interface '{name}'")
        while self.match(TokenType.NEWLINE):
            pass
        if self.match(TokenType.END):
            self.consume(TokenType.INTERFACE, "Expected 'interface' after 'End'")
        decl = StructDecl(location=start.location, name=name, fields=[], is_class=True,
                          is_interface=True, interfaces=parents)
        decl.interface_kinds = [k for k in self.generic_interfaces if k.name in parents]   # 32.4
        for method in methods:
            method.method_name, method.method_of = method.name, name
            method.name = f'{name}.{method.name}'
            method.interface_of = name
            method.parameters.insert(0, ParameterDecl(
                location=method.location, name='this', default_value=None,
                param_type=StructType(location=method.location, name=name)))
            method.changes_this = False      # set from the classes that implement it
        decl.methods = methods
        return decl

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
        # struct Pair<A, B> - a generic struct (Task 33.2b, D.166)
        type_params, conditions = self._type_parameters() if self.check(TokenType.LESS) else (None, {})

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
            # A comma: needed between fields on one line (`{ int x, int y }`); after the last
            # field of a line it isn't needed, and is ignored (Task 32.12, D.093)
            if self.match(TokenType.COMMA):
                if self.check(TokenType.NEWLINE) or self.check(closing):
                    pass
                else:
                    continue
            elif not (self.check(TokenType.NEWLINE) or self.check(closing) or self.is_at_end()) \
                    and not isinstance(item, FunctionDecl):
                raise ParserError(self.peek(), f"Fields on one line are separated by commas - "
                                               f"struct {name_token.value} {{ int x, int y }}")
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
        struct.type_params = type_params
        struct.type_conditions = conditions
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
        # class Box<T> - a generic class (Task 33.2c, D.166)
        type_params, conditions = self._type_parameters() if self.check(TokenType.LESS) else (None, {})
        interfaces, parent, parent_args = [], None, None
        self.list_element = None                   # implements List<T> (33.3d1)
        while True:
            if self.match(TokenType.IMPLEMENTS):
                interfaces += self._implements_list()
            elif self.check(TokenType.INHERITS) or (
                    self.check(TokenType.IDENTIFIER) and self.peek().value == 'extends'):
                word = self.advance()              # Task 32.7: one parent (D.084)
                if parent is not None:
                    raise ParserError(word, f"Class '{name}' has one parent - favour holding an "
                                            f"object over a second parent (D.083)")
                parent = self.consume(TokenType.IDENTIFIER, f"Expected the parent class after "
                                                            f"'{word.value}'").value
                if self.match(TokenType.LESS):     # inherits Box<T> / Box<int> - a generic parent (33.3b)
                    parent_args = [self.parse_type()]
                    while self.match(TokenType.COMMA):
                        parent_args.append(self.parse_type())
                    self.consume(TokenType.GREATER, f"Expected '>' after the types of '{parent}<...>'")
            elif self.check(TokenType.IDENTIFIER) and self.peek().value == 'includes':
                raise ParserError(self.peek(), "A class builds on a class with 'inherits' "
                                               "(or 'extends') - 'includes' is for structs")
            else:
                break
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
            # constructors public when nothing is written (files/Classes.md section 1)
            written = None              # True public, False private, 'internal' (32.2h)
            if self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.INTERNAL, TokenType.PROTECTED):
                written = {TokenType.PUBLIC: True, TokenType.PRIVATE: False,
                           TokenType.INTERNAL: 'internal',
                           TokenType.PROTECTED: 'protected'}[self.previous().type]   # 32.7
            # override / sealed / abstract before a function (Task 32.7, D.084)
            member_words = set()
            while self.check(TokenType.OVERRIDE) or self.check(TokenType.SEALED) \
                    or self.check(TokenType.ABSTRACT) or self.check(TokenType.VIRTUAL):
                word = self.advance()
                if word.type == TokenType.VIRTUAL:
                    raise ParserError(word, "Every function can be overridden - 'virtual' isn't "
                                            "needed ('sealed' stops it)")
                member_words.add(word.value)
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
            # `nocopy` / `noshare` before a field (Task 32.5b, D.034) - words only here
            copying = None
            while self.check(TokenType.IDENTIFIER) and self.peek().value in ('nocopy', 'noshare') \
                    and (self.peek(1).type == TokenType.IDENTIFIER or self.peek(1).type in self.PRIMITIVE_TYPE_TOKENS
                         or self.peek(1).value in ('nocopy', 'noshare')):
                word = self.advance().value
                if copying is not None and copying != word:
                    raise ParserError(self.previous(), "A field is nocopy or noshare, not both")
                copying = word
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
                                     written is False, written))
                continue
            item = self.parse_struct_field(signature_only='abstract' in member_words)
            if member_words and not isinstance(item, FunctionDecl):
                raise ParserError(self.previous(), f"'{sorted(member_words)[0]}' goes before a "
                                                   f"function")
            if 'abstract' in member_words and item.body is not None:
                raise ParserError(self.previous(), f"An abstract function has no code - a class "
                                                   f"that inherits it gives the code")
            if isinstance(item, FunctionDecl):
                item.is_override = 'override' in member_words
                item.is_sealed = 'sealed' in member_words
                item.is_abstract = 'abstract' in member_words
            item.is_protected = written == 'protected'
            if copying is not None and isinstance(item, FunctionDecl):
                raise ParserError(self.previous(), f"'{copying}' goes before a field")
            item.copying = copying
            item.is_internal = written == 'internal'
            item.visibility_written = written is not None
            if isinstance(item, FunctionDecl):
                item.is_private = written is False
                item.is_static = is_static
                (static_methods if is_static else methods).append(item)
                continue
            item.is_private = written is not True and written not in ('internal', 'protected')
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
                          static_fields=static_fields, static_block=static_block,
                          interfaces=interfaces, class_parent=parent)
        decl.interface_kinds = [k for k in self.generic_interfaces if k.name in interfaces]   # 32.4
        decl.class_parent_args = parent_args
        decl.type_params = type_params
        decl.type_conditions = conditions
        list_element, self.list_element = getattr(self, 'list_element', None), None
        if list_element is not None:
            decl.list_element = list_element
            methods = methods + self._list_methods(decl, methods, list_element, class_token)
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
        level = written[4] if written else None       # what was written (Task 32.2h)
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
        method.is_internal = level == 'internal'
        method.visibility_written = not written or level is not None   # one made: none needed
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

    def _list_methods(self, decl, methods: list, element, where) -> list:
        """`class Ring<T> implements List<T>` (33.3d1, D.174): the core five must be written; every other
        List method it doesn't write is added, written in Fusion from them (src/parser/list_methods.py)."""
        from src.lexer import Lexer
        from .list_methods import CORE, CORE_SHOWN, missing_text
        written = {m.name: m for m in methods}
        shown = CORE_SHOWN.replace('E ', f'{type_text(element)} ')
        lacking = [n for n in CORE if n not in written]
        wrong = [n for n, count in CORE.items() if n in written and len(written[n].parameters) != count]
        if lacking or wrong:
            what = f"has no {', '.join(lacking)}" if lacking else f"writes {', '.join(wrong)} with other parameters"
            raise ParserError(where, f"Class '{decl.name}' implements List<{type_text(element)}> but {what} - a List "
                                     f"of your own writes {shown} (D.174)")
        text = missing_text(set(written), type_text(element))
        if not text:
            return []
        added = Parser(Lexer(text, f'List<{type_text(element)}> methods').tokenize()).parse_program().declarations
        for method in added:
            method.list_default = True               # written by Fusion - a class may write its own instead
            method.is_private, method.is_static = False, False
        return added

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

        # A local or loop variable with a field's name hides the field from there to the end of its block - marked
        # `shadows_field`; the name check makes it an error unless [source] shadowing is on (47.12, D.200)
        skip = ('location', 'inferred_type', 'scope', 'declaration', 'callee_declaration', 'resolved_arguments')

        def walk(node, hidden):
            if isinstance(node, list):
                for i, item in enumerate(node):
                    node[i] = fix(item, hidden)
                    walk(node[i], hidden)
                return
            if not is_dataclass(node) or isinstance(node, type):
                return
            if isinstance(node, BlockStmt):
                local = set(hidden)
                for i, statement in enumerate(node.statements):
                    node.statements[i] = fix(statement, local)
                    walk(node.statements[i], local)
                    if isinstance(statement, VarDeclStmt) and statement.name in field_names:
                        statement.shadows_field = struct_name
                        local.add(statement.name)
                return
            inner = hidden
            if isinstance(node, ForStmt) and node.variable in field_names:
                node.shadows_field = struct_name
                inner = set(hidden) | {node.variable}
            for f in dataclass_fields(node):
                if f.name in skip:
                    continue
                value = getattr(node, f.name)
                scope = inner if f.name == 'body' else hidden
                if isinstance(value, list):
                    walk(value, scope)
                    continue
                new = fix(value, scope)
                if new is not value:
                    setattr(node, f.name, new)
                walk(new, scope)

        def fix(node, hidden):
            if isinstance(node, IdentifierExpr) and node.name in field_names and node.name not in hidden:
                return this_of(node, node.name)
            if isinstance(node, CallExpr) and isinstance(node.callee, IdentifierExpr) \
                    and node.callee.name in method_names:
                node.callee = this_of(node.callee, node.callee.name)
            return node

        walk(method.body, set())

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
        decl = EnumDecl(location=enum_token.location, name=name, variants=variants)
        while True:
            if closing != TokenType.NEWLINE:
                while self.match(TokenType.NEWLINE):
                    pass
            if self.check(closing) or self.is_at_end():
                break
            if self.match(TokenType.COMMA):
                continue
            if closing != TokenType.NEWLINE and self._enum_member_start():
                self._parse_enum_member(decl, closing)       # fields, constructor, methods (47.3)
                continue
            if decl.fields or decl.methods or decl.constructor or decl.to_string:
                raise ParserError(self.peek(), f"The values of enum '{name}' come first, then its fields "
                                               f"and functions")
            variants.append(self.parse_enum_variant(name, 0, closing))
        self._count_enum_ids(variants)

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
        self._attach_enum_methods(decl)
        return decl

    # ---- an enum as a built-in value struct (Task 47.3, D.188-D.194) ----

    def _written_id_at(self, offset: int):
        """A whole number written at peek(offset) (`200`, `-1`) - (its value, tokens it takes), or None."""
        negative = self.peek(offset).type == TokenType.MINUS
        token = self.peek(offset + 1 if negative else offset)
        if token.type != TokenType.INTEGER:
            return None
        number = integer_value(token.value)
        return (-number if negative else number), (2 if negative else 1)

    def _enum_member_start(self) -> bool:
        """A field, the constructor or a function inside an enum's block - not a value."""
        kind = self.peek().type
        if kind in (TokenType.PUBLIC, TokenType.PRIVATE, TokenType.CONST, TokenType.STATIC) \
                or kind in self.PRIMITIVE_TYPE_TOKENS:
            return True
        if kind != TokenType.IDENTIFIER:
            return False
        after = self.peek(1).type
        # `MATCH CASE` on one line are two values; `decimal mass` (an error later) and `Planet function f()` are members
        return after in (TokenType.FUNCTION, TokenType.FUNC, TokenType.LESS, TokenType.LBRACKET) or (
            after == TokenType.IDENTIFIER and self.peek().value in ('decimal', 'money', 'bytes', 'List', 'Map'))

    def _parse_enum_member(self, decl: EnumDecl, closing) -> None:
        """`public const double mass`, `private Enum(double m, ...)`, `double function gravity(...)`,
        `string function toString()` (D.190-D.192)."""
        written = None
        if self.match(TokenType.PUBLIC, TokenType.PRIVATE):
            written = self.previous().type == TokenType.PUBLIC
        while self.check(TokenType.CONST) or self.check(TokenType.STATIC):
            word = self.advance()
            if word.type == TokenType.STATIC:
                raise ParserError(word, f"An enum's fields and functions belong to each value of '{decl.name}' - "
                                        f"'static' isn't needed (the values are static already)")
        if (self.check(TokenType.ENUM) or (self.check(TokenType.IDENTIFIER) and self.peek().value == 'Enum')) \
                and self.peek(1).type == TokenType.LPAREN:          # private Enum(...) - the lexer reads Enum as enum
            start = self.advance()
            if written is not False:
                raise ParserError(start, f"An enum's constructor is private - write private Enum(...) (D.191)")
            if decl.constructor is not None:
                raise ParserError(start, f"Enum '{decl.name}' has one constructor")
            self.consume(TokenType.LPAREN, "Expected '('")
            parameters = []
            if not self.check(TokenType.RPAREN):
                parameters.append(self.parse_parameter())
                while self.match(TokenType.COMMA):
                    parameters.append(self.parse_parameter())
            self.consume(TokenType.RPAREN, "Expected ')' after the constructor's parameters")
            while self.match(TokenType.NEWLINE):
                pass
            decl.constructor = (start, parameters, self.parse_block_statement())
            return
        item = self.parse_struct_field()
        if isinstance(item, FunctionDecl):
            item.is_private = written is False
            if item.name == 'toString':
                if item.parameters:
                    raise ParserError(self.previous(), f"toString() of enum '{decl.name}' takes nothing")
                decl.to_string = item
            else:
                decl.methods.append(item)
            return
        item.is_private = written is not True       # readable from outside only when public (D.190)
        decl.fields.append(item)

    def _attach_enum_methods(self, decl: EnumDecl) -> None:
        """Each method becomes the function `Planet.gravity` with the value first, as `this`: a field's bare
        name is `this.mass`, another method's bare call `this.f(...)` (as a struct's - 32.1)."""
        field_names = {f.name for f in decl.fields} | {'id', 'enumTypeName'}
        method_names = {m.name for m in decl.methods}
        for method in decl.methods:
            if method.name in field_names or method.name in ('value', 'toInt', 'values', 'fromString', 'fromValue'):
                raise ParserError(self.previous(), f"'{method.name}' is already a field or a built-in function of "
                                                   f"enum '{decl.name}' - choose another name")
            self.rewrite_method_body(method, decl.name, field_names, method_names,
                                     lambda message: self._fail(message))
            method.method_name, method.method_of = method.name, decl.name
            method.name = f'{decl.name}.{method.name}'
            method.parameters.insert(0, ParameterDecl(
                location=method.location, name='this', default_value=None,
                param_type=StructType(location=method.location, name=decl.name)))
            method.changes_this = False
            method.enum_method = True

    def _enum_data_declared(self) -> bool:
        """After `Circle(`: data declared (`double radius`, Task 25.4) - or fixed data given (`3.3e23, ...`,
        47.3). Looks ahead only."""
        if self.check(TokenType.RPAREN):
            return True
        start = self.current
        try:
            self.parse_type()
            declared = self.check(TokenType.IDENTIFIER) and self.peek(1).type in (
                TokenType.COMMA, TokenType.RPAREN, TokenType.ASSIGN)
        except ParserError:
            declared = False
        self.current = start
        return declared

    @staticmethod
    def _count_enum_ids(variants) -> None:
        """Ids counted from 0 (D.189): a written one is used, the count goes on to the next id not used."""
        used = {v.value for v in variants if v.explicit_value}
        current = -1
        for variant in variants:
            if variant.explicit_value:
                current = variant.value
                continue
            current += 1
            while current in used:
                current += 1
            variant.value = current
            used.add(current)

    def parse_enum_variant(self, enum_name: str, default_value: int, closing=None) -> EnumVariant:
        """One enum value: `Red`, `OK = 200`, `Low = -1`, or `Number(int value)` (Task 25); its fixed data
        `EARTH(5.976e24, 6.37814e6, "Earth")` and a written id at the front or back - `200, OK`,
        `EARTH(...), 200` (Task 47.3, D.189)."""
        front = self._written_id_at(0)
        if front is not None and self.peek(front[1]).type == TokenType.COMMA:
            for _ in range(front[1] + 1):
                self.advance()
            while self.match(TokenType.NEWLINE):
                pass
        if not self.check(TokenType.IDENTIFIER):
            raise ParserError(self.peek(), f"Expected a value name in enum '{enum_name}'")
        name_token = self.advance()
        variant = EnumVariant(location=name_token.location, name=name_token.value,
                              value=default_value)
        if front is not None:
            variant.value, variant.explicit_value = front[0], True
        if self.match(TokenType.LPAREN):
            if self._enum_data_declared():
                while not self.check(TokenType.RPAREN) and not self.is_at_end():
                    variant.fields.append(self.parse_struct_field())
                    if not self.match(TokenType.COMMA):
                        break
            else:
                variant.arguments = []                       # fixed data (47.3)
                while not self.check(TokenType.RPAREN) and not self.is_at_end():
                    variant.arguments.append(self.parse_argument())
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RPAREN, f"Expected ')' after the data of '{name_token.value}'")
        back = self._written_id_at(1) if self.check(TokenType.COMMA) else None
        if back is not None and self.peek(1 + back[1]).type in (
                TokenType.NEWLINE, TokenType.DEDENT, TokenType.RBRACE, TokenType.EOF) \
                and closing != TokenType.NEWLINE:
            if front is not None:
                raise ParserError(self.peek(), f"'{name_token.value}' has its id written twice")
            for _ in range(back[1] + 1):
                self.advance()
            variant.value, variant.explicit_value = back[0], True
        if self.match(TokenType.ASSIGN):
            negative = self.match(TokenType.MINUS)
            value_token = self.consume(
                TokenType.INTEGER,
                f"The value of '{name_token.value}' must be a whole number, e.g. {name_token.value} = 200")
            variant.value = -integer_value(value_token.value) if negative else integer_value(value_token.value)
            variant.explicit_value = True
        return variant

    def parse_struct_field(self, signature_only: bool = False):
        """Parse one struct field: `int x` or `int hp = 100` (Task 18.2.1) - or a method,
        `void function move(int dx)` (Task 32.1), returned as a FunctionDecl. `byRef
        List<string> log` - shared when the struct is copied (Task 32.10a)."""
        if self.is_readonly_result_start():                      # Task 50.1 (D.110)
            return self.readonly_result(lambda: self.parse_struct_field(signature_only))
        passing = self._passing_word()
        if passing is not None:
            self.advance()
        field_type = self.parse_type()
        if self.match(TokenType.FUNCTION, TokenType.FUNC):
            return self.parse_function_declaration(field_type, signature_only=signature_only)
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

    def parse_function_declaration(self, return_type: TypeNode,
                                   signature_only: bool = False) -> ASTNode:
        """Parse function declaration: int function add(int a, int b) { body }

        Args:
            return_type: Already-parsed return type

        Returns:
            FunctionDecl AST node
        """
        func_token = self.previous()  # FUNCTION token

        # Function name (allow type keywords as function names)
        # This allows functions named "double", "string", "int", etc.
        if self.check(TokenType.IDENTIFIER) or self.is_type_start() or (
                self.peek().value in ('get', 'set') and self.peek(1).type == TokenType.LPAREN):
            # get / set: words of `property`, also a List of your own's methods (33.3d1, D.174)
            name_token = self.advance()
            name = name_token.value
            location = name_token.location
        else:
            raise ParserError(self.peek(), "Expected function name")

        # T function first<T>(...) / <K, V> / <T, T1> - its type parameters (Task 33, D.166)
        type_params, conditions = self._type_parameters() if self.check(TokenType.LESS) else (None, {})

        # Parameter list
        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                parameters.append(self.parse_parameter())

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        # An interface's function (Task 32.5a): the signature alone, unless a body follows
        if signature_only and not self.check(TokenType.COLON) and not self.check(TokenType.LBRACE) \
                and not (self.check(TokenType.NEWLINE) and self.peek(1).type == TokenType.INDENT):
            if not self.check(TokenType.DEDENT) and not self.check(TokenType.RBRACE):
                self.consume_statement_terminator()
            return FunctionDecl(location=location, return_type=return_type, name=name,
                                parameters=parameters, body=None)

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
            is_lambda=is_lambda,
            type_params=type_params,
            type_conditions=conditions
        )

    def _type_parameters(self) -> tuple:
        """`<T>`, `<K, V>`, `<T, T1>` after a generic's name (Task 33, D.166), each with an optional
        condition (33.2d, D.167): `T extends Vehicle` / `T : Vehicle` (one class, struct, `Number` or a
        basic type), `T implements Comparable, Printable` (interfaces), or both - extends first.
        After `implements` a name after a comma is one more interface, unless it is one capital letter
        (and digits) - `<T implements Comparable, K>` starts K. Returns (names, {name: (extends, [interfaces])})."""
        self.consume(TokenType.LESS, "Expected '<'")
        names, conditions = [], {}
        while True:
            token = self.consume(TokenType.IDENTIFIER, "Expected a type parameter's name - <T>, <K, V>")
            if token.value in names:
                raise ParserError(token, f"Type parameter '{token.value}' is written twice")
            names.append(token.value)
            extends, interfaces = None, []
            if self.match(TokenType.COLON) or (self.check(TokenType.IDENTIFIER) and self.peek().value == 'extends'
                                               and self.advance()):
                extends = self.parse_type()
            if self.match(TokenType.IMPLEMENTS):
                while True:
                    interfaces.append(self.consume(TokenType.IDENTIFIER, "Expected an interface after 'implements'")
                                      .value)
                    if not (self.check(TokenType.COMMA) and self.peek(1).type == TokenType.IDENTIFIER
                            and not re.match(r'^[A-Z]\d*$', self.peek(1).value)):
                        break
                    self.advance()
            if self.check(TokenType.IDENTIFIER) and self.peek().value == 'extends':
                raise ParserError(self.peek(), f"'extends' comes before 'implements' - "
                                               f"<{token.value} extends Vehicle implements Comparable>")
            if extends is not None or interfaces:
                conditions[token.value] = (extends, interfaces)
            if not self.match(TokenType.COMMA):
                break
        self.consume(TokenType.GREATER, "Expected '>' after the type parameters")
        return names, conditions

    _TYPE_ARG_TOKENS = (TokenType.IDENTIFIER, TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                        TokenType.STRING, TokenType.BOOL, TokenType.CHAR, TokenType.BYTE, TokenType.LONG, TokenType.INT128, TokenType.INT256,
                        TokenType.SHORT, TokenType.COMMA, TokenType.LBRACKET, TokenType.RBRACKET,
                        TokenType.COLON, TokenType.DOT)

    def _type_arguments_ahead(self) -> bool:
        """`first<int>(` - written types and then a call, not a comparison (`a < b`): from the '<' to
        its '>' only type words, then '('."""
        depth, i = 0, 0
        while i < 64:
            token = self.peek(i)
            if token.type == TokenType.LESS:
                depth += 1
            elif token.type == TokenType.GREATER:
                depth -= 1
                if depth == 0:          # first<int>( ... or Box<int>.made - a copy's static (33.3c)
                    after = self.peek(i + 1)
                    return after.type == TokenType.LPAREN or (
                        after.type == TokenType.DOT and self.peek(i + 2).type == TokenType.IDENTIFIER)
            elif token.type not in self._TYPE_ARG_TOKENS:
                return False
            i += 1
        return False

    def _type_arguments(self) -> list:
        """The types written at a call - `first<int>(...)`, `valueOf<string, int>(...)` (D.166)."""
        self.consume(TokenType.LESS, "Expected '<'")
        types = [self.parse_type()]
        while self.match(TokenType.COMMA):
            types.append(self.parse_type())
        self.consume(TokenType.GREATER, "Expected '>' after the types")
        return types
