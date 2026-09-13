"""
Recursive Descent Parser for Fusion Programming Language

This module implements a parser that converts a token stream into an Abstract
Syntax Tree (AST). Uses precedence climbing for binary operators.
"""

import json
from typing import List, Optional
from src.lexer.token import Token, TokenType, SourceLocation
from src.parser.ast_nodes import *


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
        return self.parse_or()

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

    def parse_equality(self) -> ASTNode:
        """Parse equality: expr == expr, expr != expr

        Precedence: 6
        Associativity: Left

        Returns:
            Expression AST node
        """
        expr = self.parse_relational()

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous().value
            right = self.parse_relational()
            expr = BinaryExpr(
                location=expr.location,
                left=expr,
                operator=operator,
                right=right
            )

        return expr

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

        return self.parse_call()

    def parse_call(self) -> ASTNode:
        """Parse function calls: func(arg1, arg2, ...)

        Precedence: 1 (postfix operator)

        Returns:
            Expression AST node (CallExpr or primary expression)
        """
        expr = self.parse_primary()

        # Handle multiple chained calls: func()()
        while self.match(TokenType.LPAREN):
            arguments = []

            # Parse argument list
            if not self.check(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    arguments.append(self.parse_expression())

            self.consume(TokenType.RPAREN, "Expected ')' after function arguments")

            expr = CallExpr(
                location=expr.location,
                callee=expr,
                arguments=arguments
            )

        return expr

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions: literals, identifiers, parentheses, lambdas.

        Precedence: 1 (highest)

        Returns:
            Expression AST node

        Raises:
            ParserError: If token is not a valid primary expression
        """
        # Integer literal
        if self.match(TokenType.INTEGER):
            token = self.previous()
            return LiteralExpr(
                location=token.location,
                value=int(token.value),
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
                value=token.value,
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

        # Identifier (allow type keywords and END as identifiers in expression context)
        # This allows calling functions/variables named "double", "string", "end", etc.
        if self.check(TokenType.IDENTIFIER) or self.is_type_start() or self.check(TokenType.END):
            # Only consume if it's actually a valid identifier context
            # (not followed by another type keyword or invalid syntax)
            token = self.advance()
            return IdentifierExpr(
                location=token.location,
                name=token.value
            )

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

        # Parse lambda body (single expression for MVP)
        body = self.parse_expression()

        # Return type is inferred for MVP (placeholder void for now)
        return LambdaExpr(
            location=start_loc,
            parameters=parameters,
            return_type=PrimitiveType(start_loc, name="void"),  # Will be inferred later
            body=body
        )

    def parse_parameter(self) -> ParameterDecl:
        """Parse function/lambda parameter: type name = default_value

        Returns:
            ParameterDecl AST node
        """
        # Parse type (for now, just expect identifier for type name)
        param_type = self.parse_type()

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
            param_type=param_type,
            name=name,
            default_value=default_value
        )

    def parse_type(self) -> TypeNode:
        """Parse type annotation: int, float, double, string, bool, char, void

        Returns:
            TypeNode (PrimitiveType for MVP)
        """
        # For MVP, only support primitive types
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                      TokenType.STRING, TokenType.BOOL, TokenType.CHAR,
                      TokenType.VOID):
            token = self.previous()
            return PrimitiveType(
                location=token.location,
                name=token.value
            )

        raise ParserError(
            self.peek(),
            f"Expected type name, got '{self.peek().value}'"
        )

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
        segments: List[Union[StringTextPart, StringExprPart]] = []
        has_interpolation = False

        for part_type, part_value in parts:
            if part_type == "STRING_PART":
                segments.append(StringTextPart(text=part_value))
            elif part_type in ("INTERP_VAR", "INTERP_POS", "INTERPOLATION"):
                # INTERP_VAR: {varname}, INTERP_POS: {@1}, INTERPOLATION: legacy
                has_interpolation = True
                # Tokenize and parse the embedded expression
                from src.lexer.lexer import Lexer
                lexer = Lexer(part_value, token.location.filename)
                expr_tokens = lexer.tokenize()
                expr_parser = Parser(expr_tokens)
                segments.append(StringExprPart(expression=expr_parser.parse_expression()))

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

        # Check if it's a variable declaration (starts with type)
        if self.is_type_start():
            return self.parse_var_declaration()

        # Otherwise, parse as expression (could be assignment)
        expr = self.parse_expression()

        # Check for assignment: expr = value
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
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

        # Optional initializer
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        self.consume_statement_terminator()

        return VarDeclStmt(
            location=location,
            var_type=var_type,
            name=name,
            initializer=initializer
        )

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

        self.consume_statement_terminator()

        return VarDeclStmt(
            location=location,
            var_type=var_type,
            name=name,
            initializer=initializer,
            is_const=True
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
        condition = self.parse_expression()

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

    def parse_while_statement(self) -> ASTNode:
        """Parse while loop: while condition { body }

        Returns:
            WhileStmt AST node
        """
        while_token = self.previous()  # WHILE token

        # Condition
        condition = self.parse_expression()

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
        # Consume any newline tokens (optional)
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
            TokenType.VOID
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

        while not self.is_at_end():
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)

            # Skip newlines between declarations
            while self.match(TokenType.NEWLINE):
                pass

        return ProgramNode(
            location=start_loc,
            declarations=declarations
        )

    def parse_declaration(self) -> Optional[ASTNode]:
        """Parse top-level declaration (function, var, etc.).

        Returns:
            Declaration AST node or None if no valid declaration found

        Raises:
            ParserError: If declaration is malformed
        """
        # Function declaration: <return_type> function <name>(<params>) { body }
        if self.is_type_start():
            return_type = self.parse_type()

            # Skip newlines after return type
            while self.match(TokenType.NEWLINE):
                pass

            if self.match(TokenType.FUNCTION):
                return self.parse_function_declaration(return_type)

            # Could be a global variable declaration
            # For MVP, we might not support global vars
            raise ParserError(self.peek(), "Expected 'function' keyword after type")

        # Skip unexpected tokens (error recovery)
        raise ParserError(self.peek(), f"Unexpected token '{self.peek().value}' at top level")

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
