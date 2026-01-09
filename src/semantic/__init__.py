"""Semantic analysis package.

This package provides semantic analysis capabilities for the Fusion compiler,
including symbol table management, type checking, name resolution, and validation.

Exports:
    - SemanticAnalyzer: Main analyzer class
    - SemanticError: Exception for semantic errors
    - Symbol: Represents a symbol (variable, function, parameter)
    - Scope: Represents a single scope level
    - SymbolTable: Manages scopes and symbol resolution
"""

from .errors import SemanticError
from .symbol import Symbol, Scope
from .symbol_table import SymbolTable
from .semantic_analyzer import SemanticAnalyzer

__all__ = ['SemanticAnalyzer', 'SemanticError', 'Symbol', 'Scope', 'SymbolTable']
