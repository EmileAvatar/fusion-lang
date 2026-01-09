"""
Fusion Parser Module

This module contains the parser and AST node definitions for the Fusion compiler.
"""

from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import (
    # Base
    ASTNode,
    # Expressions
    LiteralExpr,
    IdentifierExpr,
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    LambdaExpr,
    InterpolatedStringExpr,
    # Statements
    ExpressionStmt,
    VarDeclStmt,
    AssignmentStmt,
    IfStmt,
    WhileStmt,
    ForStmt,
    ReturnStmt,
    BlockStmt,
    # Declarations
    ParameterDecl,
    FunctionDecl,
    ProgramNode,
    # Types
    TypeNode,
    PrimitiveType,
    FunctionType,
)

__all__ = [
    # Parser
    'Parser',
    'ParserError',
    # Base
    'ASTNode',
    # Expressions
    'LiteralExpr',
    'IdentifierExpr',
    'BinaryExpr',
    'UnaryExpr',
    'CallExpr',
    'LambdaExpr',
    'InterpolatedStringExpr',
    # Statements
    'ExpressionStmt',
    'VarDeclStmt',
    'AssignmentStmt',
    'IfStmt',
    'WhileStmt',
    'ForStmt',
    'ReturnStmt',
    'BlockStmt',
    # Declarations
    'ParameterDecl',
    'FunctionDecl',
    'ProgramNode',
    # Types
    'TypeNode',
    'PrimitiveType',
    'FunctionType',
]
