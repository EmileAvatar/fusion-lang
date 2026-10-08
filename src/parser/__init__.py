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
    StringTextPart,
    StringExprPart,
    ArrayLiteralExpr,
    IndexExpr,
    MemberExpr,
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
    StructField,
    StructDecl,
    ProgramNode,
    # Types
    TypeNode,
    PrimitiveType,
    FunctionType,
    ArrayType,
    StructType,
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
    'StringTextPart',
    'StringExprPart',
    'ArrayLiteralExpr',
    'IndexExpr',
    'MemberExpr',
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
    'StructField',
    'StructDecl',
    'ProgramNode',
    # Types
    'TypeNode',
    'PrimitiveType',
    'FunctionType',
    'ArrayType',
    'StructType',
]
